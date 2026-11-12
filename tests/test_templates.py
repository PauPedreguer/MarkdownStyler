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

    def test_publica_les_variables_doc(self):
        """La plantilla ha de publicar les metadades com a variables --doc-*."""
        for variable in (
            "--doc-institut",
            "--doc-departament",
            "--doc-assignatura",
            "--doc-curs",
            "--doc-data",
        ):
            self.assertIn(variable, self.plantilla)


class TestPrintStyles(unittest.TestCase):
    """Comprova les regles d'impressió/PDF de styles/prova.css."""

    def setUp(self):
        self.css = from_project_root("styles", "prova.css").read_text(encoding="utf-8")

    def test_portada_i_index_samaguen_nomes_en_pantalla(self):
        """Les regles que amaguen portada/índex han de viure dins @media screen.

        Si s'apliquen també en imprimir, la portada i l'índex no s'imprimeixen.
        """
        bloc = self.css[self.css.index("@media screen {"):self.css.index("@media print {")]
        self.assertIn(".pdf-cover", bloc)
        self.assertIn(".pdf-toc", bloc)

    def test_capcalera_de_pantalla_oculta_en_imprimir(self):
        """En imprimir, la capçalera gran de pantalla no s'ha de mostrar."""
        bloc = self.css[self.css.index("@media print {"):]
        self.assertIn("Capçalera de pantalla: FORA de la impressió", bloc)
        seccio = bloc[bloc.index("Capçalera de pantalla"):][:400]
        self.assertRegex(seccio, r"\.header,[\s\S]*?display:\s*none !important")

    def test_capcaleres_i_peus_de_pagina(self):
        """@page ha de portar capçaleres/peus amb les variables --doc-*."""
        self.assertIn("@page {", self.css)
        self.assertIn("content: var(--doc-institut)", self.css)
        self.assertIn("content: var(--doc-departament)", self.css)
        self.assertIn('counter(page) " de " counter(pages)', self.css)

    def test_portada_sense_marges_ni_peus(self):
        """@page:first (portada) no ha de portar marges ni capçaleres."""
        bloc = self.css[self.css.index("@page:first"):]
        self.assertIn("margin: 0", bloc)
        self.assertIn("content: none", bloc)

    def test_paginacio_evita_talls_dolents(self):
        """Cal controlar vídues/òrfenes i repetir la capçalera de les taules."""
        self.assertIn("orphans: 3", self.css)
        self.assertIn("widows: 3", self.css)
        self.assertIn("display: table-header-group", self.css)


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
