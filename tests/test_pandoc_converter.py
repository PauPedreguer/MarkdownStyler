"""Tests unitaris per al convertidor de Pandoc."""
import subprocess
import tempfile
import unittest
from pathlib import Path
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
        captured = {}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "base.css").write_text("/* BASE STYLES */", encoding="utf-8")
            (tmp / "pdf.css").write_text("/* PDF SPECIFIC STYLES */", encoding="utf-8")

            def fake_root(*parts):
                """Resol qualsevol ruta del projecte dins del directori temporal."""
                return tmp / Path(*parts).name

            def fake_run(cmd, **kwargs):
                # Capturar el contingut del fitxer CSS temporal abans que s'elimini
                css_args = [arg for arg in cmd if arg.startswith("--css=")]
                if css_args:
                    temp_path = css_args[0].split("=", 1)[1]
                    captured["content"] = Path(temp_path).read_text(encoding="utf-8")

            with mock.patch.object(pandoc_converter.subprocess, "run", side_effect=fake_run) as mock_run, \
                 mock.patch.object(pandoc_converter, "from_project_root", side_effect=fake_root):
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
        # Ha de contenir un únic --css amb un fitxer temporal concatenat
        css_args = [arg for arg in cmd if arg.startswith("--css=")]
        self.assertEqual(len(css_args), 1)
        # El fitxer temporal ha de contenir el contingut de pdf.css i de base.css
        self.assertIn("PDF SPECIFIC STYLES", captured["content"])
        self.assertIn("BASE STYLES", captured["content"])

    def test_html_concatenates_base_and_selected_css(self):
        """El CSS temporal de l'HTML ha de combinar base.css i l'estil triat."""
        captured = {}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "base.css").write_text("/* BASE STYLES */", encoding="utf-8")
            (tmp / "prova.css").write_text("/* EDU DOCS STYLE */", encoding="utf-8")

            def fake_root(*parts):
                return tmp / Path(*parts).name

            def fake_run(cmd, **kwargs):
                css_args = [arg for arg in cmd if arg.startswith("--css=")]
                if css_args:
                    temp_path = css_args[0].split("=", 1)[1]
                    captured["content"] = Path(temp_path).read_text(encoding="utf-8")

            with mock.patch.object(pandoc_converter.subprocess, "run", side_effect=fake_run), \
                 mock.patch.object(pandoc_converter, "from_project_root", side_effect=fake_root):
                pandoc_converter.convert_markdown(
                    md_path=self.md_path,
                    output_path=self.output_path,
                    css_path=self.css_path,
                    template_path=self.template_path,
                    js_path=self.js_path,
                    highlight_style=self.highlight_style,
                    metadata=self.metadata,
                )

        self.assertIn("BASE STYLES", captured["content"])
        self.assertIn("EDU DOCS STYLE", captured["content"])
        # L'estil específic s'ha de carregar després del base
        self.assertLess(
            captured["content"].index("BASE STYLES"),
            captured["content"].index("EDU DOCS STYLE"),
        )

    def test_js_path_is_passed_as_metadata(self):
        """El JS de la plantilla s'afig a les metadades per al template."""
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
        self.assertTrue(any(arg.startswith("--metadata=js:") for arg in cmd))
        self.assertTrue(any(arg.startswith("--resource-path=") for arg in cmd))




class TestPostprocessMermaid(unittest.TestCase):
    """Comprova el postprocessat dels blocs mermaid."""

    def test_converteix_blocs_de_codi_en_divs(self):
        """Un <pre class="sourceCode mermaid"> esdevé <div class="mermaid">."""
        html = (
            '<div class="sourceCode" id="cb1">'
            '<pre class="sourceCode mermaid"><code class="sourceCode mermaid">'
            "graph TD;\n  A--&gt;B;"
            "</code></pre></div>"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_path = Path(tmp_dir) / "doc.html"
            html_path.write_text(html, encoding="utf-8")

            pandoc_converter._postprocess_mermaid(str(html_path))

            resultat = html_path.read_text(encoding="utf-8")

        self.assertIn('<div class="mermaid">', resultat)
        self.assertIn("A-->B;", resultat)
        self.assertNotIn("sourceCode", resultat)

    def test_fitxer_inexistent_no_falla(self):
        """Si pandoc no ha generat el fitxer, el postprocessat no ha de petar."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            inexistent = Path(tmp_dir) / "no-generat.html"

            pandoc_converter._postprocess_mermaid(str(inexistent))

            self.assertFalse(inexistent.exists())


class TestPandocErrors(unittest.TestCase):
    """Comprova la propagació d'errors de Pandoc."""

    def setUp(self):
        self.kwargs = dict(
            md_path="examen.md",
            output_path="out/examen.html",
            css_path="styles/prova.css",
            template_path="templates/base.html",
            js_path="scripts/script.js",
            highlight_style="zenburn",
            metadata={"title": "Examen"},
        )

    def test_error_de_pandoc_inclou_stderr(self):
        """L'error ha de conservar el missatge que ha emès Pandoc."""
        error = subprocess.CalledProcessError(
            1, ["pandoc"], stderr="pandoc: no s'ha trobat examen.md"
        )
        with mock.patch.object(pandoc_converter.subprocess, "run", side_effect=error):
            with self.assertRaises(pandoc_converter.PandocError) as ctx:
                pandoc_converter.convert_markdown(**self.kwargs)

        self.assertIn("no s'ha trobat examen.md", str(ctx.exception))
        self.assertIn("no s'ha trobat examen.md", ctx.exception.stderr)
        self.assertEqual(ctx.exception.stderr, "pandoc: no s'ha trobat examen.md")

    def test_avisos_de_pandoc_no_son_errors(self):
        """Un stderr amb avisos i codi 0 no ha de llançar cap excepció."""
        with mock.patch.object(
            pandoc_converter.subprocess,
            "run",
            return_value=mock.MagicMock(stderr="[WARNING] color-mix ignorat"),
        ):
            pandoc_converter.convert_markdown(**self.kwargs)


if __name__ == "__main__":
    unittest.main()
