"""Test d'integració de la generació de PDF (Chromium + Pandoc + poppler).

Es salta automàticament si falta qualsevol de les eines, perquè la suite no ha
de fallar en entorns sense navegador.
"""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main
from src.infrastructure.config_repo import load_institut_config

MD = """# Document de prova

Text d'exemple amb `codi`.

## Primera secció

Més text.
"""


def _disponible(ordre: str) -> bool:
    """Indica si una ordre del sistema està al PATH."""
    return shutil.which(ordre) is not None


@unittest.skipUnless(main.navegador_chromium(), "Cal un navegador Chromium")
@unittest.skipUnless(_disponible("pandoc"), "Cal pandoc")
@unittest.skipUnless(
    _disponible("pdfinfo") and _disponible("pdftotext"), "Cal poppler-utils"
)
class TestGeneraPdf(unittest.TestCase):
    """Comprova el PDF generat: portada, índex, capçaleres i peus."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.md = cls.tmp / "document.md"
        cls.md.write_text(MD, encoding="utf-8")
        # Es prova el camí complet del CLI (el que fa servir pdf.sh)
        cls.codi = main.main(
            ["--pdf", str(cls.md), "--out", str(cls.tmp), "--title", "Prova PDF"]
        )
        cls.pdf = cls.tmp / "document.pdf"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _text(self, pagina: int) -> str:
        """Retorna el text d'una pàgina del PDF (base 1)."""
        resultat = subprocess.run(
            [
                "pdftotext",
                "-layout",
                "-f",
                str(pagina),
                "-l",
                str(pagina),
                str(self.pdf),
                "-",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return resultat.stdout

    def _pagines(self) -> int:
        info = subprocess.run(
            ["pdfinfo", str(self.pdf)], capture_output=True, text=True, check=True
        ).stdout
        return int(re.search(r"Pages:\s+(\d+)", info).group(1))

    def test_genera_html_i_pdf(self):
        """El CLI ha de deixar l'HTML i el PDF a la carpeta indicada."""
        self.assertEqual(self.codi, 0)
        self.assertTrue(self.pdf.is_file())
        self.assertTrue(self.pdf.with_suffix(".html").is_file())

    def test_te_portada_i_index(self):
        """Portada (pàgina 1) i índex (pàgina 2)."""
        self.assertGreaterEqual(self._pagines(), 2)
        self.assertIn("Índex", self._text(2))

    def test_la_portada_no_porta_peu_de_pagina(self):
        """@page:first no ha de mostrar el comptador de pàgines."""
        self.assertNotIn("Pàgina 1 de", self._text(1))

    def test_la_resta_porta_peu_i_capcalera(self):
        """La pàgina 2 ha de portar el comptador i el departament del centre."""
        text = self._text(2)
        self.assertIn("Pàgina 2 de", text)
        departament = load_institut_config().get("departament", "")
        if departament:
            self.assertIn(departament, text)

    def test_fitxer_inexistent_retorna_error(self):
        """Si el Markdown no existeix, el CLI ha de tornar codi 1."""
        codi = main.main(
            ["--pdf", str(self.tmp / "no-existeix.md"), "--out", str(self.tmp)]
        )
        self.assertEqual(codi, 1)

    def test_pdf_sense_fitxer_es_error_d_us(self):
        """--pdf sense fitxer ha de fallar amb l'ajuda del CLI."""
        with self.assertRaises(SystemExit):
            main.main(["--pdf"])


class TestNavegadorChromium(unittest.TestCase):
    """Comprova la detecció del navegador."""

    def test_detecta_el_navegador_del_sistema(self):
        """Si hi ha cap navegador dels coneguts, s'ha de detectar."""
        if not any(shutil.which(nom) for nom in main.NAVEGADORS):
            self.skipTest("No hi ha cap navegador Chromium instal·lat")
        self.assertIsNotNone(main.navegador_chromium())

    def test_retorna_none_si_no_hi_ha_navegador(self):
        """Sense cap navegador al PATH, la detecció ha de tornar None."""
        with mock.patch.object(main.shutil, "which", return_value=None):
            self.assertIsNone(main.navegador_chromium())


if __name__ == "__main__":
    unittest.main()
