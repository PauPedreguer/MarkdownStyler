"""Tests unitaris per al cas d'ús execute_export."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.core.models import ExportOptions
from src.use_cases import generate_html


class TestExecuteExport(unittest.TestCase):
    """Comprova la lògica d'exportació."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        # Crear un fitxer markdown de prova
        self.md_file = self.tmp_path / "examen.md"
        self.md_file.write_text("# Examen\n", encoding="utf-8")

        self.mock_config = {
            "css_name": "prova.css",
            "template_name": "base.html",
            "js_name": "script.js",
            "highlight_style": "zenburn",
            "institut_nom": "IES Test",
            # Mode presentació (també arriba a la plantilla com a metadades).
            "presentacio_nivell": 2,
            "presentacio_modus": "diapositives",
            "presentacio_tema": "fosc",
            # El primer color de la taula de Configuració és el document per
            # defecte: d'ahí ixen el curs i l'assignatura de la capçalera.
            "identitats": [
                {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
                {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
            ],
        }

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_export_html_uses_correct_extension(self):
        """L'exportació ha de generar un fitxer .html."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            result = generate_html.execute_export(options)

        self.assertTrue(result.endswith(".html"))
        self.assertEqual(Path(result).name, "examen.html")
        mock_convert.assert_called_once()

    def test_metadata_includes_user_options(self):
        """Les metadades han d'incloure les opcions de l'usuari."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Títol Prova",
            curs_academic="26-27",
            subtitol="Subtítol",
            departament="Matemàtiques",
            primary_color="#166534",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        call_kwargs = mock_convert.call_args.kwargs
        metadata = call_kwargs["metadata"]
        self.assertEqual(metadata["title"], "Títol Prova")
        self.assertEqual(metadata["data"], "26-27")
        self.assertEqual(metadata["subtitol"], "Subtítol")
        self.assertEqual(metadata["departament"], "Matemàtiques")
        self.assertEqual(metadata["primary_color"], "#166534")

    def test_metadata_includes_config(self):
        """Les metadades han d'incloure la configuració de l'institut."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        call_kwargs = mock_convert.call_args.kwargs
        metadata = call_kwargs["metadata"]
        self.assertEqual(metadata["institut_nom"], "IES Test")
        self.assertEqual(metadata["highlight_style"], "zenburn")

    def test_metadata_includes_presentation_settings(self):
        """El mode presentació es configura des de la finestra i arriba a l'HTML."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertEqual(metadata["presentacio_nivell"], 2)
        self.assertEqual(metadata["presentacio_modus"], "diapositives")
        self.assertEqual(metadata["presentacio_tema"], "fosc")

    def test_metadata_uses_config_departament_when_empty(self):
        """Si no s'indica departament, s'ha de respectar el de la configuració."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        config = {**self.mock_config, "departament": "Matemàtiques"}
        with mock.patch.object(generate_html, "load_institut_config", return_value=config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertEqual(metadata["departament"], "Matemàtiques")

    def test_metadata_agafa_el_curs_i_l_assignatura_del_color(self):
        """El curs i l'assignatura del color triat manen sobre el defecte."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
            curs="2n DAW",
            assignatura="DWEC",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertEqual(metadata["curs"], "2n DAW")
        self.assertEqual(metadata["assignatura"], "DWEC")
        # El curs acadèmic (26-27) no es toca: són dades distintes.
        self.assertEqual(metadata["data"], "26-27")

    def test_la_paleta_no_arriba_a_pandoc(self):
        """Els colors d'identitat són dades de l'aplicació, no de la plantilla.

        Si s'envien com a metadades, pandoc els posa a la línia d'ordres com un
        text amb claudàtors i cometes que cap plantilla pot aprofitar.
        """
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        config = {
            **self.mock_config,
            "identitats": [{"color": "#166534", "curs": "1r DAW", "assignatura": "LMSGI"}],
        }
        with mock.patch.object(generate_html, "load_institut_config", return_value=config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertNotIn("identitats", metadata)
        self.assertEqual(metadata["institut_nom"], config["institut_nom"])

    def test_metadata_usa_el_curs_i_l_assignatura_de_la_config_si_van_buits(self):
        """Un color sense identitat deixa manar el primer color de la taula."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
        )
        config = {
            **self.mock_config,
            "identitats": [
                {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
            ],
        }
        with mock.patch.object(generate_html, "load_institut_config", return_value=config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertEqual(metadata["curs"], "1r DAW")
        self.assertEqual(metadata["assignatura"], "LMSGI")


if __name__ == "__main__":
    unittest.main()
