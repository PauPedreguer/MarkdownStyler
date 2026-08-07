"""Tests unitaris per al convertidor de Pandoc."""
import unittest
from unittest import mock

from src.infrastructure import pandoc_converter


class TestPandocConverter(unittest.TestCase):
    """Comprova la construcció de la comanda de Pandoc."""

    def setUp(self):
        self.md_path = "examen.md"
        self.output_path = "out/examen.html"
        self.css_path = "styles/prova.css"
        self.template_path = "templates/base.html"
        self.js_path = "scripts/script.js"
        self.highlight_style = "zenburn"
        self.metadata = {"title": "Examen", "data": "01-01-2026"}

    def test_html_export_uses_katex(self):
        """L'exportació HTML ha d'usar --katex."""
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path=self.output_path,
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style=self.highlight_style,
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        self.assertIn("--katex", cmd)
        self.assertNotIn("--pdf-engine=weasyprint", cmd)

    def test_pdf_export_uses_weasyprint(self):
        """L'exportació PDF ha d'usar weasyprint i --webtex."""
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path="out/examen.pdf",
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style=self.highlight_style,
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        self.assertIn("--pdf-engine=weasyprint", cmd)
        self.assertIn("--webtex", cmd)
        self.assertNotIn("--katex", cmd)

    def test_metadata_is_passed(self):
        """Les metadades s'han de passar com a --metadata."""
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path=self.output_path,
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style=self.highlight_style,
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        self.assertIn("--metadata=title:Examen", cmd)
        self.assertIn("--metadata=data:01-01-2026", cmd)

    def test_highlight_style_is_passed(self):
        """L'estil de ressaltat s'ha de passar correctament."""
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path=self.output_path,
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style="tango",
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        self.assertIn("--highlight-style=tango", cmd)

    def test_pdf_uses_pdf_css(self):
        """L'exportació PDF ha d'usar styles/pdf.css si existeix."""
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run, \
             mock.patch.object(pandoc_converter.Path, "exists", return_value=True):
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path="out/examen.pdf",
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style=self.highlight_style,
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        # Ha de contenir la ruta absoluta a styles/pdf.css
        self.assertTrue(any("pdf.css" in arg for arg in cmd))


if __name__ == "__main__":
    unittest.main()
