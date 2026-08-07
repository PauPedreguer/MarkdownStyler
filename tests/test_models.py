"""Tests unitaris per al model ExportOptions."""
import unittest

from src.core.models import ExportOptions


class TestExportOptions(unittest.TestCase):
    """Comprova el comportament del dataclass ExportOptions."""

    def test_defaults(self):
        """Els valors per defecte han de ser correctes."""
        opts = ExportOptions(
            md_path="examen.md",
            output_dir="/tmp",
            title="Examen",
            data="01-01-2026",
        )
        self.assertEqual(opts.subtitol, "")
        self.assertEqual(opts.departament, "Informàtica")
        self.assertEqual(opts.primary_color, "#1d4ed8")
        self.assertEqual(opts.format, "html")

    def test_custom_values(self):
        """Els valors personalitzats s'han de respectar."""
        opts = ExportOptions(
            md_path="examen.md",
            output_dir="/tmp",
            title="Examen",
            data="01-01-2026",
            subtitol="Pràctica 1",
            departament="Matemàtiques",
            primary_color="#166534",
            format="pdf",
        )
        self.assertEqual(opts.subtitol, "Pràctica 1")
        self.assertEqual(opts.departament, "Matemàtiques")
        self.assertEqual(opts.primary_color, "#166534")
        self.assertEqual(opts.format, "pdf")

    def test_fields_are_accessible(self):
        """Tots els camps han de ser accessibles com a atributs."""
        opts = ExportOptions(
            md_path="a.md",
            output_dir="out",
            title="T",
            data="d",
        )
        self.assertEqual(opts.md_path, "a.md")
        self.assertEqual(opts.output_dir, "out")
        self.assertEqual(opts.title, "T")
        self.assertEqual(opts.data, "d")


if __name__ == "__main__":
    unittest.main()
