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

# Document pensat per a forçar la fragmentació amb una finestra menuda: la
# primera secció té un sol apartat i un paràgraf que no hi cap (no hi ha cap
# tall net: la diapositiva ha de fer scroll), i la segona en té dos (sí que es
# pot tallar davant del segon apartat).
MD_LLARG = (
    "# Document llarg\n\n"
    "## Un sol apartat\n\n"
    "### L'apartat\n\n"
    + "Text de prova que no cap en una pantalla. " * 60
    + "\n\n## Dos apartats\n\n"
    "### Primer\n\n"
    + "Més text de prova per a omplir la pantalla. " * 24
    + "\n\n### Segon\n\n"
    + "Text final de la segona part. " * 24
    + "\n"
)


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

    def _dom(
        self,
        ruta: Path,
        hash_: str = "",
        mida: str = "1400,900",
        args: tuple[str, ...] = (),
    ) -> str:
        """Retorna el DOM que deixa el navegador després d'executar el JS."""
        resultat = subprocess.run(
            [
                self.navegador,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--window-size=" + mida,
                "--virtual-time-budget=6000",
                "--dump-dom",
                *args,
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

    def _dom_amb_script(
        self,
        js: str,
        nom: str = "mesura",
        fitxer: Path | None = None,
        hash_: str = "",
        mida: str = "1400,900",
        args: tuple[str, ...] = (),
    ) -> str:
        """DOM després d'executar un script propi al final del document.

        `--dump-dom` només torna HTML, així que el script deixa el resultat en
        un atribut de <html> i el test el llig d'allí. Va amb l'esdeveniment
        `load` perquè els listeners de script.js ja estiguen enganxats.

        `args` passa opcions extra al navegador: les proves de scroll forcen
        `--force-prefers-reduced-motion` perquè els desplaçaments siguen
        instantanis i la mesura no depenga de l'animació.
        """
        base = Path(fitxer) if fitxer else self.html
        cap, cua = base.read_text(encoding="utf-8").rsplit("</body>", 1)
        desti = self.tmp / f"{nom}.html"
        desti.write_text(
            cap + f"<script>{js}</script></body>" + cua, encoding="utf-8"
        )
        return self._dom(desti, hash_, mida, args)

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
        """El ☾ de la cantonada canvia el tema del document, no un de propi."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const fosc = () => document.documentElement.classList.contains('tema-fosc');
    const dades = {};
    document.getElementById('presentacio-toggle').click();
    dades.mode = document.body.classList.contains('mode-presentacio');
    const boto = document.getElementById('tema-toggle');
    dades.dinsDelPeu = Boolean(document.querySelector('.presentacio-peu #tema-toggle'));
    dades.visible = getComputedStyle(boto).display !== 'none';
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
        # El tema no es repetix al peu: continua a la cantonada, com sempre.
        self.assertTrue(dades["visible"])
        self.assertFalse(dades["dinsDelPeu"])
        self.assertTrue(dades["fosc"])
        self.assertEqual(dades["desat"], "fosc")
        self.assertEqual(dades["fonsDiapo"], "rgb(11, 18, 32)")
        # En eixir es restauren la capçalera i el sumari, però no el tema.
        self.assertFalse(dades["modeDespres"])
        self.assertTrue(dades["foscDespres"])

    def test_el_peu_porta_quatre_botons_d_icona(self):
        """◀ ▶ ? ✕ són SVG (sense glifs) i el tema i el ⛶ queden a dalt."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    document.getElementById('presentacio-toggle').click();
    const boto = Array.from(document.querySelectorAll('.presentacio-peu button'));
    // El botó d'ajuda (el tercer) ha d'obrir el panell; es tanca tot seguit
    // perquè la resta de mesures no el tinguen a sobre.
    boto[2].click();
    const panell = document.querySelector('.presentacio-ajuda-panel');
    const ajudaOberta = Boolean(panell && !panell.hidden);
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    const caixa = (id) => {
        const node = document.getElementById(id);
        const r = node.getBoundingClientRect();
        const mig = document.elementFromPoint(
            r.left + r.width / 2, r.top + r.height / 2
        );
        return {
            visible: getComputedStyle(node).display !== 'none',
            dalt: Math.round(r.top),
            dreta: Math.round(window.innerWidth - r.right),
            ample: Math.round(r.width),
            perDamunt: Boolean(mig && node.contains(mig))
        };
    };
    document.documentElement.setAttribute('data-prova', JSON.stringify({
        quants: boto.length,
        totesAmbIcona: boto.every((node) => Boolean(node.querySelector('svg'))),
        senseText: boto.every((node) => node.textContent.trim() === ''),
        etiquetes: boto.map((node) => node.getAttribute('aria-label')),
        ajudaOberta: ajudaOberta,
        tema: caixa('tema-toggle'),
        pantalla: caixa('fullscreen-toggle'),
        ajuda: caixa('presentacio-toggle')
    }));
});
""",
            "peu-icones",
        )
        dades = self._dades_del_dom(dom)
        self.assertEqual(dades["quants"], 4)
        self.assertTrue(dades["totesAmbIcona"], dades["etiquetes"])
        self.assertTrue(dades["senseText"], dades["etiquetes"])
        # El botó d'ajuda obri el panell de tecles (i Esc el tanca).
        self.assertTrue(dades["ajudaOberta"])
        self.assertEqual(
            [etiqueta.split(" (")[0] for etiqueta in dades["etiquetes"]],
            [
                "Diapositiva anterior",
                "Diapositiva següent",
                "Tecles de la presentació",
                "Eixir de la presentació",
            ],
        )
        # El tema i la pantalla completa viuen a la cantonada, no al peu, i
        # queden per damunt del contingut (que en presentació és fix).
        self.assertTrue(dades["tema"]["visible"])
        self.assertTrue(dades["pantalla"]["visible"])
        self.assertTrue(dades["tema"]["perDamunt"], dades["tema"])
        self.assertTrue(dades["pantalla"]["perDamunt"], dades["pantalla"])
        self.assertEqual((dades["tema"]["ample"], dades["pantalla"]["ample"]), (38, 38))
        self.assertEqual(dades["tema"]["dalt"], 16)
        self.assertEqual(dades["pantalla"]["dreta"], 16)
        self.assertEqual(dades["tema"]["dreta"], 16 + 38 + 8)
        # I el ▶ d'iniciar la presentació ja no cal dins de la presentació.
        self.assertFalse(dades["ajuda"]["visible"])
    def test_el_titol_de_la_diapositiva_ix_centrat(self):
        """El títol va centrat (sense barra) i el cos continua a l'esquerra."""
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    document.getElementById('presentacio-toggle').click();
    // Un h2 de secció (no la portada): és el que duia barra i marge.
    const titol = document.querySelector('.slide:not(.slide-portada) .slide-titol');
    const diapo = titol.closest('.slide');
    const rang = document.createRange();
    rang.selectNodeContents(titol);
    const text = rang.getBoundingClientRect();
    const caixa = diapo.getBoundingClientRect();
    const cos = diapo.querySelector('.slide-cos h3');
    document.documentElement.setAttribute('data-prova', JSON.stringify({
        alineacio: getComputedStyle(titol).textAlign,
        paddingEsquerre: getComputedStyle(titol).paddingLeft,
        abans: getComputedStyle(titol, '::before').content,
        centreText: Math.round(text.left + text.width / 2),
        centreDiapo: Math.round(caixa.left + caixa.width / 2),
        cos: cos ? getComputedStyle(cos).textAlign : null
    }));
});
""",
            "titol-centrat",
        )
        dades = self._dades_del_dom(dom)
        self.assertEqual(dades["alineacio"], "center")
        self.assertEqual(dades["paddingEsquerre"], "0px")
        # La barra vertical del h2 (base.css) ha de desaparéixer.
        self.assertEqual(dades["abans"], "none")
        self.assertLessEqual(abs(dades["centreText"] - dades["centreDiapo"]), 2, dades)
        # El contingut de la diapositiva no canvia d'alineació.
        self.assertIn(dades["cos"], {"start", "left"})

    def test_cap_diapositiva_no_acaba_en_un_encapcalament(self):
        """En tallar, cap títol queda sol: o va amb el seu contingut o la
        diapositiva fa scroll."""
        md = self.tmp / "llarg.md"
        md.write_text(MD_LLARG, encoding="utf-8")
        html = Path(
            execute_export(
                ExportOptions(
                    md_path=str(md),
                    output_dir=str(self.tmp),
                    title="Prova llarga",
                    curs_academic="26-27",
                )
            )
        )
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const dades = Array.from(document.querySelectorAll('.slide')).map((diapo) => {
        const fills = Array.from(diapo.querySelector('.slide-cos').children);
        return {
            ultim: fills.length ? fills[fills.length - 1].tagName.toLowerCase() : null,
            primer: fills.length ? fills[0].tagName.toLowerCase() : null,
            cont: Boolean(diapo.querySelector('.slide-cont')),
            desborda: diapo.classList.contains('desborda')
        };
    });
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "talls",
            fitxer=html,
            hash_="#presentar",
            mida="1000,400",
        )
        dades = self._dades_del_dom(dom)
        titols = {"h1", "h2", "h3", "h4", "h5", "h6"}
        # Cap diapositiva no acaba amb un encapçalament sol.
        self.assertEqual([dada for dada in dades if dada["ultim"] in titols], [])
        # El paràgraf que no cap amb el seu apartat fa scroll en compte de
        # deixar el títol orfe.
        self.assertTrue(any(dada["desborda"] for dada in dades), dades)
        # On sí que hi ha tall net, la continuació comença per un apartat.
        continuacions = [dada for dada in dades if dada["cont"]]
        self.assertTrue(continuacions, dades)
        self.assertTrue(
            any(dada["primer"] in titols for dada in continuacions), continuacions
        )

    def test_en_eixir_els_titols_recuperen_l_espai_del_document(self):
        """Entrar i eixir no deixa els títols amb l'estil de la presentació.

        La primera diapositiva de cada grup aprofita el títol original, així
        que en eixir s'hi ha de llevar `slide-titol`: si es queda, els marges
        del document no tornen mai (marge zero, text centrat i sense barra).
        """
        dom = self._dom_amb_script(
            """
window.addEventListener('load', () => {
    const portada = document.querySelector('.content h1');
    const titol = document.querySelector('.content h2');
    const mesura = (node) => {
        const estil = getComputedStyle(node);
        return {
            classe: node.className,
            margeDalt: estil.marginTop,
            margeBaix: estil.marginBottom,
            farcitDalt: estil.paddingTop,
            alineacio: estil.textAlign,
            barra: getComputedStyle(node, '::before').content
        };
    };
    const abans = { h1: mesura(portada), h2: mesura(titol) };
    document.getElementById('presentacio-toggle').click();
    const durant = mesura(titol);
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
    document.documentElement.setAttribute('data-prova', JSON.stringify({
        abans: abans,
        durant: durant,
        despres: { h1: mesura(portada), h2: mesura(titol) },
        marques: document.querySelectorAll(
            '.content .slide-titol, .content .slide-cont'
        ).length
    }));
});
""",
            "titols-restaurats",
        )
        dades = self._dades_del_dom(dom)
        # Dins de la presentació el títol sí que va centrat i sense marge...
        self.assertEqual(dades["durant"]["alineacio"], "center")
        self.assertEqual(dades["durant"]["margeDalt"], "0px")
        # ...i en eixir torna exactament a l'estat d'abans d'entrar.
        self.assertEqual(dades["marques"], 0, dades["despres"])
        self.assertEqual(dades["despres"]["h1"], dades["abans"]["h1"])
        self.assertEqual(dades["despres"]["h2"], dades["abans"]["h2"])
        self.assertNotIn("slide-titol", dades["despres"]["h2"]["classe"])
        # La barra del h2 hi torna (base.css): no és només qüestió de marges.
        self.assertNotEqual(dades["abans"]["h2"]["barra"], "none")

    def test_en_mode_scroll_les_fletxes_mouen_la_pagina_poc_a_poc(self):
        """En scroll, ↓/↑ i Re/Av Pàg desplacen la pàgina sense canviar de
        secció (en diapositives sí que salten de diapositiva)."""
        ruta = self._html_amb(modus="scroll")
        dom = self._dom_amb_script(
            """
const espera = (ms) => new Promise((t) => setTimeout(t, ms));
window.addEventListener('load', async () => {
    const contingut = document.querySelector('.content');
    const polsa = (key) => document.dispatchEvent(
        new KeyboardEvent('keydown', { key: key, bubbles: true })
    );
    document.getElementById('presentacio-toggle').click();
    await espera(400);
    const dades = { alt: contingut.clientHeight, passos: [] };
    contingut.scrollTo({ top: 0, behavior: 'auto' });
    await espera(150);
    for (const tecla of ['ArrowDown', 'ArrowDown', 'PageDown', 'ArrowUp']) {
        const abans = contingut.scrollTop;
        polsa(tecla);
        await espera(350);
        dades.passos.push({
            tecla: tecla,
            pas: Math.round(contingut.scrollTop - abans)
        });
    }
    dades.total = contingut.scrollHeight;
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "scroll-fi",
            fitxer=ruta,
            mida="1200,400",
            args=("--force-prefers-reduced-motion",),
        )
        dades = self._dades_del_dom(dom)
        alt = dades["alt"]
        self.assertGreater(alt, 0)
        self.assertGreater(dades["total"], alt * 2, dades)
        quarts = dades["passos"][:2]
        for pas in quarts:
            self.assertTrue(
                0.2 <= pas["pas"] / alt <= 0.3,
                f"un quart de pantalla, no una secció: {dades}",
            )
        pagina = dades["passos"][2]
        self.assertEqual(pagina["tecla"], "PageDown")
        self.assertTrue(
            0.8 <= pagina["pas"] / alt <= 0.9,
            f"Av Pàg ha de fer prop d'una pantalla: {dades}",
        )
        enrere = dades["passos"][3]
        self.assertEqual(enrere["tecla"], "ArrowUp")
        self.assertTrue(
            -0.3 <= enrere["pas"] / alt <= -0.2,
            f"↑ ha de tornar arrere un quart: {dades}",
        )

    def test_en_mode_scroll_l_espai_salta_de_seccio(self):
        """En scroll, Espai continua saltant a la secció següent."""
        ruta = self._html_amb(modus="scroll")
        dom = self._dom_amb_script(
            """
const espera = (ms) => new Promise((t) => setTimeout(t, ms));
window.addEventListener('load', async () => {
    const contingut = document.querySelector('.content');
    document.getElementById('presentacio-toggle').click();
    await espera(400);
    contingut.scrollTo({ top: 0, behavior: 'auto' });
    await espera(150);
    const segona = document.querySelectorAll('.slide')[1].offsetTop;
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: ' ', bubbles: true })
    );
    await espera(400);
    document.documentElement.setAttribute('data-prova', JSON.stringify({
        segona: segona,
        posicio: contingut.scrollTop,
        comptador: document.querySelector('.presentacio-comptador').textContent,
        total: document.querySelectorAll('.slide').length
    }));
});
""",
            "scroll-espai",
            fitxer=ruta,
            mida="1200,400",
            args=("--force-prefers-reduced-motion",),
        )
        dades = self._dades_del_dom(dom)
        self.assertLessEqual(abs(dades["posicio"] - dades["segona"]), 2, dades)
        self.assertEqual(dades["comptador"], f"2 / {dades['total']}")

    def test_en_mode_diapositives_les_fletxes_canvien_de_diapositiva(self):
        """Fora del mode scroll, ↓ continua passant de diapositiva."""
        dom = self._dom_amb_script(
            """
const espera = (ms) => new Promise((t) => setTimeout(t, ms));
window.addEventListener('load', async () => {
    const contingut = document.querySelector('.content');
    const comptador = () => document.querySelector(
        '.presentacio-comptador'
    ).textContent;
    const polsa = (key) => document.dispatchEvent(
        new KeyboardEvent('keydown', { key: key, bubbles: true })
    );
    document.getElementById('presentacio-toggle').click();
    await espera(400);
    polsa('Home');
    await espera(400);
    const dades = { abans: comptador() };
    polsa('ArrowDown');
    await espera(400);
    dades.despres = comptador();
    dades.posicio = contingut.scrollTop;
    dades.segona = document.querySelectorAll('.slide')[1].offsetTop;
    document.documentElement.setAttribute('data-prova', JSON.stringify(dades));
});
""",
            "diapos-fletxes",
            args=("--force-prefers-reduced-motion",),
        )
        dades = self._dades_del_dom(dom)
        self.assertTrue(dades["abans"].startswith("1 / "), dades)
        self.assertTrue(dades["despres"].startswith("2 / "), dades)
        self.assertLessEqual(abs(dades["posicio"] - dades["segona"]), 2, dades)


if __name__ == "__main__":
    unittest.main()