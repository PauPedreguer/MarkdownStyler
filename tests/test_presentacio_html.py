"""Test d'integració del mode presentació (Pandoc + navegador real).

Genera un HTML de veres, l'obri amb Chromium headless i comprova que el
document es convertix en diapositives quan s'activa el mode. Es salta
automàticament si falta Pandoc o el navegador.
"""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
from html import unescape
from pathlib import Path

import main
from src.core.models import ExportOptions
from src.use_cases.generate_html import execute_export

MD = """# Document de prova

Text d'entrada.

## Primera secció

Text de la primera secció.

### Un apartat

Més text de l'apartat.

## Segona secció

- Un element
- Un altre element

## Tercera secció

| Columna | Valor |
| --- | --- |
| a | 1 |
"""


def _disponible(ordre: str) -> bool:
    """Indica si una ordre del sistema està al PATH."""
    return shutil.which(ordre) is not None


@unittest.skipUnless(main.navegador_chromium(), "Cal un navegador Chromium")
@unittest.skipUnless(_disponible("pandoc"), "Cal pandoc")
class TestPresentacioHtml(unittest.TestCase):
    """Comprova el mode presentació sobre l'HTML ja generat."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.md = cls.tmp / "presentacio.md"
        cls.md.write_text(MD, encoding="utf-8")
        cls.html = Path(
            execute_export(
                ExportOptions(
                    md_path=str(cls.md),
                    output_dir=str(cls.tmp),
                    title="Prova presentació",
                    curs_academic="26-27",
                )
            )
        )
        cls.navegador = main.navegador_chromium()

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _dom(self, ruta: Path, hash_: str = "") -> str:
        """Retorna el DOM que deixa el navegador després d'executar el JS."""
        resultat = subprocess.run(
            [
                self.navegador,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--window-size=1400,900",
                "--virtual-time-budget=6000",
                "--dump-dom",
                ruta.as_uri() + hash_,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
        return resultat.stdout

    def _html_amb(self, **canvis: str) -> Path:
        """Còpia de l'HTML amb els atributs data-presentacio-* canviats."""
        html = self.html.read_text(encoding="utf-8")
        for clau, valor in canvis.items():
            antic = re.search(rf'data-presentacio-{clau}="[^"]*"', html)
            self.assertIsNotNone(antic)
            html = html.replace(antic.group(0), f'data-presentacio-{clau}="{valor}"')
        desti = self.tmp / f"canviat-{'-'.join(canvis.values())}.html"
        desti.write_text(html, encoding="utf-8")
        return desti

    def _dom_amb_script(self, js: str, nom: str = "mesura") -> str:
        """DOM després d'executar un script propi al final del document.

        `--dump-dom` només torna HTML, així que el script deixa el resultat en
        un atribut de <html> i el test el llig d'allí. Va amb l'esdeveniment
        `load` perquè els listeners de script.js ja estiguen enganxats.
        """
        cap, cua = self.html.read_text(encoding="utf-8").rsplit("</body>", 1)
        desti = self.tmp / f"{nom}.html"
        desti.write_text(
            cap + f"<script>{js}</script></body>" + cua, encoding="utf-8"
        )
        return self._dom(desti)

    def _dades_del_dom(self, dom: str, atribut: str = "data-prova") -> dict:
        """Recupera el JSON que el script de mesura ha deixat a <html>."""
        trobat = re.search(rf'{atribut}="([^"]*)"', dom)
        self.assertIsNotNone(trobat, "el script de mesura no ha deixat dades")
        return json.loads(unescape(trobat.group(1)))

    def test_l_html_porta_el_boto_el_css_i_el_script(self):
        """Els tres recursos han d'acabar incrustats al document."""
        html = self.html.read_text(encoding="utf-8")
        self.assertIn('id="presentacio-toggle"', html)
        self.assertIn('data-presentacio-nivell="2"', html)
        self.assertIn("MODE PRESENTACIÓ", html)
        self.assertIn("presentacio-peu", html)

    def test_activar_converteix_el_document_en_diapositives(self):
        """Amb #presentar hi ha portada, diapositives i comptador."""
        dom = self._dom(self.html, "#presentar")
        self.assertIn('class="slide slide-portada"', dom)
        self.assertGreaterEqual(dom.count('<section class="slide'), 4)
        self.assertRegex(dom, r'class="presentacio-comptador"[^>]*>1 / \d+<')

    def test_no_duplica_identificadors(self):
        """Els títols de continuació no poden repetir ids (HTML vàlid)."""
        dom = self._dom(self.html, "#presentar")
        ids = re.findall(r'\sid="([^"]+)"', dom)
        repetits = [clau for clau, cops in Counter(ids).items() if cops > 1]
        self.assertEqual(repetits, [])

    def test_el_mode_scroll_no_fragmenta_les_seccions(self):
        """En scroll hi ha exactament portada + una diapositiva per ##."""
        ruta = self._html_amb(modus="scroll")
        dom = self._dom(ruta, "#presentar")
        self.assertNotIn('<span class="slide-cont">', dom)
        self.assertEqual(dom.count('<section class="slide'), 1 + MD.count("\n## "))

    def test_els_botons_flotants_formen_una_fila_horitzontal(self):
        """▶ ⛶ ☾ ⌃ pengen de la capçalera, enganxats i en una sola fila."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const ids = ['presentacio-toggle', 'fullscreen-toggle', 'tema-toggle', 'header-toggle'];
    const dades = ids.map((id) => {
        const node = document.getElementById(id);
        if (!node) return { id: id, falta: true };
        const r = node.getBoundingClientRect();
        return {
            id: id,
            top: Math.round(r.top),
            right: Math.round(r.right),
            ample: Math.round(r.width),
            alt: Math.round(r.height),
            visible: getComputedStyle(node).display !== 'none'
        };
    });
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "fila",
        )
        dades = self._dades_del_dom(dom)
        self.assertEqual(
            [dada["id"] for dada in dades],
            ["presentacio-toggle", "fullscreen-toggle", "tema-toggle", "header-toggle"],
        )
        for dada in dades:
            self.assertNotIn("falta", dada, dada)
            self.assertTrue(dada["visible"], dada)
            self.assertEqual((dada["ample"], dada["alt"]), (40, 40), dada)
        # Una sola fila: tots pengen de la mateixa alçada...
        self.assertEqual(len({dada["top"] for dada in dades}), 1, dades)
        # ...i es toquen: 40 px de separació entre vores dretes consecutives.
        for esquerre, dret in zip(dades, dades[1:]):
            self.assertEqual(esquerre["right"] + 40, dret["right"], dades)

    def test_el_boto_de_tema_canvia_el_document_i_el_desa(self):
        """☾ passa el document sencer a fosc i ho recorda (localStorage)."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const fons = () => getComputedStyle(document.body).backgroundColor;
    const fosc = () => document.documentElement.classList.contains('tema-fosc');
    const dades = {
        inicial: fosc() ? 'fosc' : 'clar',
        fonsInicial: fons()
    };
    document.getElementById('tema-toggle').click();
    dades.despres = fosc() ? 'fosc' : 'clar';
    dades.fonsDespres = fons();
    dades.desat = localStorage.getItem('markdownstyler-tema');
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "tema",
        )
        dades = self._dades_del_dom(dom)
        # Primer colp: clar (el tema inicial per defecte).
        self.assertEqual(dades["inicial"], "clar")
        self.assertEqual(dades["despres"], "fosc")
        self.assertEqual(dades["desat"], "fosc")
        self.assertEqual(dades["fonsInicial"], "rgb(244, 246, 249)")
        self.assertEqual(dades["fonsDespres"], "rgb(11, 18, 32)")

    def test_la_presentacio_hereta_el_tema_i_no_el_guarda_en_eixir(self):
        """La T del peu canvia el tema del document, no un de la presentació."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const fosc = () => document.documentElement.classList.contains('tema-fosc');
    const dades = {};
    document.getElementById('presentacio-toggle').click();
    dades.mode = document.body.classList.contains('mode-presentacio');
    const boto = Array.from(document.querySelectorAll('.presentacio-peu button'))
        .find((node) => node.textContent.trim() === 'T');
    dades.teBoto = Boolean(boto);
    boto.click();
    dades.fosc = fosc();
    dades.fonsDiapo = getComputedStyle(document.querySelector('.content')).backgroundColor;
    dades.desat = localStorage.getItem('markdownstyler-tema');
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    dades.modeDespres = document.body.classList.contains('mode-presentacio');
    dades.foscDespres = fosc();
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "tema-presentacio",
        )
        dades = self._dades_del_dom(dom)
        self.assertTrue(dades["mode"])
        self.assertTrue(dades["teBoto"])
        self.assertTrue(dades["fosc"])
        self.assertEqual(dades["desat"], "fosc")
        self.assertEqual(dades["fonsDiapo"], "rgb(11, 18, 32)")
        # En eixir es restauren la capçalera i el sumari, però no el tema.
        self.assertFalse(dades["modeDespres"])
        self.assertTrue(dades["foscDespres"])


if __name__ == "__main__":
    unittest.main()