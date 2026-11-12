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
        }

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_export_html_uses_correct_extension(self):
        """L'exportació HTML ha de generar un fitxer .html."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
            format="html",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            result = generate_html.execute_export(options)

        self.assertTrue(result.endswith(".html"))
        self.assertEqual(Path(result).name, "examen.html")
        mock_convert.assert_called_once()

    def test_export_pdf_uses_correct_extension(self):
        """L'exportació PDF ha de generar un fitxer .pdf."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
            format="pdf",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            result = generate_html.execute_export(options)

        self.assertTrue(result.endswith(".pdf"))
        self.assertEqual(Path(result).name, "examen.pdf")

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
            format="html",
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
            format="html",
        )
        with mock.patch.object(generate_html, "load_institut_config", return_value=self.mock_config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        call_kwargs = mock_convert.call_args.kwargs
        metadata = call_kwargs["metadata"]
        self.assertEqual(metadata["institut_nom"], "IES Test")
        self.assertEqual(metadata["highlight_style"], "zenburn")

    def test_metadata_uses_config_departament_when_empty(self):
        """Si no s'indica departament, s'ha de respectar el de la configuració."""
        options = ExportOptions(
            md_path=str(self.md_file),
            output_dir=str(self.tmp_path),
            title="Examen",
            curs_academic="26-27",
            format="html",
        )
        config = {**self.mock_config, "departament": "Matemàtiques"}
        with mock.patch.object(generate_html, "load_institut_config", return_value=config), \
             mock.patch.object(generate_html, "convert_markdown") as mock_convert:
            generate_html.execute_export(options)

        metadata = mock_convert.call_args.kwargs["metadata"]
        self.assertEqual(metadata["departament"], "Matemàtiques")


if __name__ == "__main__":
    unittest.main()
