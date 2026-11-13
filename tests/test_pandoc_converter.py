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
        """L'exportació ha d'usar --katex i no cap motor de PDF."""
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
        self.assertIn("--embed-resources", cmd)
        self.assertFalse(any(arg.startswith("--pdf-engine") for arg in cmd))

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

    def test_highlight_style_theme_file_is_passed_as_absolute_path(self):
        """Un tema propi (.theme) s'ha de passar com a ruta absoluta.

        Pandoc només reconeix els noms dels temes que porta incorporats; per a
        un tema del projecte cal donar-li el camí del fitxer.
        """
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(
                md_path=self.md_path,
                output_path=self.output_path,
                css_path=self.css_path,
                template_path=self.template_path,
                js_path=self.js_path,
                highlight_style="themes/one-dark.theme",
                metadata=self.metadata,
            )
        cmd = mock_run.call_args.args[0]
        estil = [arg for arg in cmd if arg.startswith("--highlight-style=")]
        self.assertEqual(len(estil), 1)
        ruta = estil[0].split("=", 1)[1]
        self.assertTrue(ruta.startswith("/"), ruta)
        self.assertTrue(ruta.endswith("themes/one-dark.theme"), ruta)
        self.assertTrue(Path(ruta).is_file(), ruta)

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


class TestCssMetadata(unittest.TestCase):
    """Comprova l'escapat de metadades que es publiquen com a CSS."""

    def test_escapa_cometes_barres_i_salts(self):
        """Cometes, barres invertides i salts de línia s'han d'escapar."""
        self.assertEqual(pandoc_converter._css_escape('a"b'), 'a\\"b')
        self.assertEqual(pandoc_converter._css_escape("a\\b"), "a\\\\b")
        self.assertEqual(pandoc_converter._css_escape("a\nb"), "a b")
        self.assertEqual(pandoc_converter._css_escape("a\r\nb"), "a b")
        self.assertEqual(pandoc_converter._css_escape(None), "")

    def test_afegeix_les_claus_css_a_les_metadades(self):
        """Les metadades --doc-* han d'arribar escapades a pandoc."""
        metadata = {"institut_nom": 'IES "Prova"', "departament": "Informàtica"}
        with mock.patch.object(pandoc_converter.subprocess, "run") as mock_run:
            pandoc_converter.convert_markdown(**{**self.kwargs(), "metadata": metadata})

        cmd = mock_run.call_args.args[0]
        self.assertIn('--metadata=institut_nom_css:IES \\"Prova\\"', cmd)
        self.assertIn("--metadata=departament_css:Informàtica", cmd)
        # Les metadades originals no es toquen (van a l'HTML)
        self.assertIn('--metadata=institut_nom:IES "Prova"', cmd)

    @staticmethod
    def kwargs():
        return dict(
            md_path="examen.md",
            output_path="out/examen.html",
            css_path="styles/prova.css",
            template_path="templates/base.html",
            js_path="scripts/script.js",
            highlight_style="zenburn",
        )


class TestRecursosDePresentacio(unittest.TestCase):
    """Comprova que el CSS i el JS del mode presentació arriben a Pandoc."""

    def _executa(self) -> dict:
        """Executa la conversió amb Pandoc simulat i recull la comanda i el CSS."""
        capturat: dict = {}

        def _run(cmd, **_kwargs):
            capturat["cmd"] = cmd
            for argument in cmd:
                if argument.startswith("--css="):
                    capturat["css"] = Path(argument.split("=", 1)[1]).read_text(
                        encoding="utf-8"
                    )
            return mock.MagicMock(stderr="")

        with mock.patch.object(pandoc_converter.subprocess, "run", side_effect=_run):
            pandoc_converter.convert_markdown(
                md_path="examen.md",
                output_path="out/examen.html",
                css_path="styles/prova.css",
                template_path="templates/base.html",
                js_path="scripts/script.js",
                highlight_style="zenburn",
                metadata={"title": "Examen"},
            )
        return capturat

    def test_el_css_de_presentacio_va_despres_de_l_estil_triat(self):
        """Així pot sobreescriure'l sense tocar-lo (tot va sota un mode)."""
        css = self._executa()["css"]
        self.assertIn("MODE PRESENTACIÓ", css)
        self.assertLess(
            css.index("EDU DOCS STYLE"), css.index("MODE PRESENTACIÓ")
        )

    def test_el_script_de_presentacio_va_a_les_metadades(self):
        """La plantilla necessita la ruta per a $if(presentacio_js)$."""
        cmd = self._executa()["cmd"]
        metadades = [arg for arg in cmd if arg.startswith("--metadata=presentacio_js:")]
        self.assertEqual(len(metadades), 1)
        self.assertTrue(metadades[0].endswith("presentacio.js"))


if __name__ == "__main__":
    unittest.main()
