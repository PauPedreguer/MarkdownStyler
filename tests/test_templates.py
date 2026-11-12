"""Tests de la plantilla HTML i del script de suport.

Comproven invariants que afecten la validesa de l'HTML generat (ids duplicats
del sumari) i el ressaltat de codi (el fa pandoc, no highlight.js).
"""
import unittest

from src.infrastructure.project_paths import from_project_root


class TestBaseTemplate(unittest.TestCase):
    """Comprova la plantilla templates/base.html."""

    def setUp(self):
        self.plantilla = from_project_root("templates", "base.html").read_text(
            encoding="utf-8"
        )

    def test_toc_apareix_una_sola_vegada(self):
        """El $toc$ s'ha de generar una única vegada (barra lateral).

        L'índex d'impressió es clona per JS perquè, si es generara dos cops amb
        pandoc, els ids ``toc-*`` quedarien duplicats al DOM.
        """
        self.assertEqual(self.plantilla.count("$toc$"), 1)

    def test_injecta_el_css_de_ressaltat_de_pandoc(self):
        """Cal incloure $highlighting-css$ i abans del full d'estil propi."""
        self.assertIn("$highlighting-css$", self.plantilla)
        self.assertLess(
            self.plantilla.index("$highlighting-css$"),
            self.plantilla.index('href="$css$"'),
        )

    def test_no_carrega_highlight_js(self):
        """Ja no s'ha de carregar highlight.js (ho fa pandoc)."""
        self.assertNotIn("highlight.min.js", self.plantilla)


class TestScriptJs(unittest.TestCase):
    """Comprova scripts/script.js."""

    def setUp(self):
        self.script = from_project_root("scripts", "script.js").read_text(
            encoding="utf-8"
        )

    def test_no_usa_highlight_js(self):
        """El script no ha de cridar hljs."""
        self.assertNotIn("hljs", self.script)

    def test_clona_el_sumari_traent_els_ids(self):
        """La còpia de l'índex per a impressió s'ha de fer sense ids."""
        self.assertIn(".pdf-toc .toc", self.script)
        self.assertIn("removeAttribute('id')", self.script)

    def test_els_desplegables_nomes_afecten_la_barra_lateral(self):
        """Els toggles del sumari només s'han d'aplicar al sidebar."""
        self.assertIn("'.sidebar .toc li'", self.script)

    def test_highlight_min_js_esborrat(self):
        """La llibreria highlight.js (121 KB) ja no ha d'existir."""
        self.assertFalse(from_project_root("scripts", "highlight.min.js").exists())


if __name__ == "__main__":
    unittest.main()
