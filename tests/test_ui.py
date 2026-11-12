"""Tests unitaris de la interfície que no necessiten QApplication.

Només es comproven funcions pures i helpers importables: no es crea cap
finestra ni cap diàleg (els tests han de córrer sense entorn gràfic).
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main
from src.core.models import ExportOptions
from src.infrastructure.highlight_styles import (
    ESTIL_RESSALTAT_DEFECTE,
    ESTILS_PROJECTE,
    ESTILS_RESSALTAT,
)
from src.infrastructure.project_paths import from_project_root
from src.ui.app import App
from src.ui.components.settings_dialog import (
    CSS_NO_SELECCIONABLES,
    JS_NO_SELECCIONABLES,
    recursos_disponibles,
)
from src.ui.components.success_dialog import url_fitxer


class FakeAppQt:
    """Substitut mínim de QApplication que anota l'orde de les crides."""

    def __init__(self):
        self.calls = []

    def setStyle(self, nom):
        self.calls.append(("style", nom))

    def setStyleSheet(self, qss):
        self.calls.append(("qss", qss))


class TestAplicaTema(unittest.TestCase):
    """Comprova l'aplicació del tema de la interfície."""

    def test_fixa_fusion_abans_de_carregar_el_qss(self):
        """L'estil Fusion s'ha de fixar abans del full QSS, no després."""
        fake = FakeAppQt()

        main.aplica_tema(fake)

        self.assertEqual([crida[0] for crida in fake.calls], ["style", "qss"])
        self.assertEqual(fake.calls[0][1], "Fusion")

    def test_qss_es_llegeix_en_utf8(self):
        """El QSS s'ha de llegir en UTF-8 i no amb el locale del sistema."""
        fake = FakeAppQt()

        main.aplica_tema(fake)

        esperat = from_project_root("src", "ui", "style.qss").read_text(encoding="utf-8")
        self.assertEqual(fake.calls[1][1], esperat)


class TestUrlFitxer(unittest.TestCase):
    """Comprova la construcció d'URLs file:// del diàleg d'èxit."""

    def test_escapa_espais_i_accents(self):
        """Els espais i accents han d'anar escapats a la URL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            fitxer = Path(tmp_dir) / "Pràctica 1 (examen).html"
            fitxer.write_text("<html></html>", encoding="utf-8")

            url = url_fitxer(str(fitxer))

        self.assertTrue(url.startswith("file:///"))
        self.assertIn("%20", url)
        self.assertNotIn(" ", url)
        self.assertTrue(url.endswith("Pr%C3%A0ctica%201%20%28examen%29.html"))


class TestRecursosDisponibles(unittest.TestCase):
    """Comprova que els combos d'ajustos no oferisquen fitxers de suport."""

    def test_exclou_els_css_de_suport(self):
        """base.css no ha d'aparèixer com a estil seleccionable."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            for nom in ("base.css", "prova.css", "estil-examen.css"):
                (Path(tmp_dir) / nom).write_text("/* */", encoding="utf-8")

            noms = recursos_disponibles(Path(tmp_dir), ".css", CSS_NO_SELECCIONABLES)

        self.assertEqual(noms, ["estil-examen.css", "prova.css"])

    def test_exclou_llibreries_js(self):
        """highlight.min.js no s'ha d'oferir com a script de la plantilla."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            for nom in ("highlight.min.js", "script.js", "toc.js"):
                (Path(tmp_dir) / nom).write_text("//", encoding="utf-8")

            noms = recursos_disponibles(Path(tmp_dir), ".js", JS_NO_SELECCIONABLES)

        self.assertEqual(noms, ["script.js", "toc.js"])

    def test_directori_inexistent_retorna_llista_buida(self):
        """Si el directori no existeix, la llista ha de ser buida."""
        self.assertEqual(
            recursos_disponibles(
                Path("/tmp/no-existeix-aquest-directori"), ".css", frozenset()
            ),
            [],
        )


class TestEstilsRessaltat(unittest.TestCase):
    """Comprova la llista d'estils de ressaltat que oferix el diàleg d'ajustos.

    El bloc de codi té fons fosc (#1e293b), així que només els temes foscos es
    llegixen bé. La llista ha de dir a l'usuari quin és quin i no ha d'oferir
    els temes clars de pandoc, que deixen el codi quasi d'un sol color.
    """

    def test_one_dark_es_el_primer_i_el_recomanat(self):
        """One Dark és el tema per defecte: ha d'anar primer i marcat."""
        estil, etiqueta = ESTILS_RESSALTAT[0]
        self.assertEqual(estil, ESTIL_RESSALTAT_DEFECTE)
        self.assertEqual(estil, "themes/one-dark.theme")
        self.assertIn("fosc", etiqueta)
        self.assertIn("recomanat", etiqueta)

    def test_els_temes_del_projecte_van_primer(self):
        """Els temes propis s'ofereixen abans que els de pandoc."""
        valors = [estil for estil, _ in ESTILS_RESSALTAT]
        propis = [ruta for ruta, _ in ESTILS_PROJECTE]
        self.assertEqual(valors[:len(propis)], propis)

    def test_els_valors_son_unics(self):
        """Els valors desats al desplegable no es poden repetir."""
        valors = [estil for estil, _ in ESTILS_RESSALTAT]
        self.assertEqual(len(valors), len(set(valors)))

    def test_les_etiquetes_diuen_que_el_tema_es_fosc(self):
        """Cada etiqueta ha d'avisar del tema, per a no triar-ne un de clar."""
        for estil, etiqueta in ESTILS_RESSALTAT:
            self.assertIn("fosc", etiqueta, estil)

    def test_els_temes_clars_de_pandoc_no_s_oferixen(self):
        """Els temes de fons clar fan el codi il·legible sobre el bloc fosc."""
        valors = {estil for estil, _ in ESTILS_RESSALTAT}
        self.assertEqual(valors & {"pygments", "tango", "kate", "haddock"}, set())



class TestExportThread(unittest.TestCase):
    """Comprova que el fil d'exportació no llig widgets de Qt."""

    def setUp(self):
        self.options = ExportOptions(
            md_path="examen.md",
            output_dir="/tmp",
            title="Examen",
            curs_academic="26-27",
        )
        self.fake_self = mock.MagicMock()

    def test_nomes_rep_les_opcions_i_emete_senyal(self):
        """El fil ha d'usar les opcions rebudes, no tornar a llegir widgets."""
        with mock.patch(
            "src.ui.app.execute_export", return_value="/tmp/examen.html"
        ) as mock_exec:
            App._export_thread(self.fake_self, self.options)

        mock_exec.assert_called_once_with(self.options)
        self.fake_self.signals.finished.emit.assert_called_once_with("/tmp/examen.html")

    def test_emet_error_si_l_exportacio_falla(self):
        """Un error d'exportació s'ha de comunicar pel senyal d'error."""
        with mock.patch(
            "src.ui.app.execute_export", side_effect=RuntimeError("pandoc ha fallat")
        ):
            App._export_thread(self.fake_self, self.options)

        self.fake_self.signals.error.emit.assert_called_once_with("pandoc ha fallat")


if __name__ == "__main__":
    unittest.main()
