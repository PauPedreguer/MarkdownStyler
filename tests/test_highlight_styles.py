"""Tests dels estils de ressaltat de codi (``--highlight-style``).

Cada tema propi (``themes/*.theme``) ha de ser un JSON de skylighting vàlid, ha
de donar color a tots els tokens i ha de mantindre un contrast mínim de 4.5:1
sobre el fons del bloc de codi: per davall d'eixe valor els tokens es perden i
el codi torna a semblar d'un sol color (el problema que tenia zenburn).
"""
import contextlib
import io
import json
import shutil
import subprocess
import unittest

from src.infrastructure.config_repo import DEFAULT_CONFIG
from src.infrastructure.highlight_styles import (
    ESTIL_RESSALTAT_DEFECTE,
    ESTILS_PANDOC,
    ESTILS_PROJECTE,
    ESTILS_RESSALTAT,
    ruta_estil_ressaltat,
)
from src.infrastructure.project_paths import from_project_root

# Fons del bloc de codi (styles/base.css): els temes propis s'hi afinen.
FONS = "#1e293b"

# Mínim de WCAG AA per a text normal.
CONTRAST_MINIM = 4.5


def _llumineria(hexa: str) -> float:
    """Llumineria relativa (WCAG) d'un color ``#rrggbb``."""
    digits = hexa.lstrip("#")
    canals = [int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    canals = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
              for c in canals]
    return 0.2126 * canals[0] + 0.7152 * canals[1] + 0.0722 * canals[2]


def _contrast(color: str, fons: str) -> float:
    """Ràtio de contrast entre dos colors ``#rrggbb``."""
    l1, l2 = _llumineria(color), _llumineria(fons)
    clar, fosc = max(l1, l2), min(l1, l2)
    return (clar + 0.05) / (fosc + 0.05)


def _tema(ruta: str) -> dict:
    """Carrega el JSON d'un tema del projecte."""
    return json.loads(from_project_root(ruta).read_text(encoding="utf-8"))



class TestFitxersDeTema(unittest.TestCase):
    """Comprova els fitxers ``themes/*.theme``."""

    def test_els_tres_temes_existeixen(self):
        """Cada tema oferit ha de tindre el seu fitxer al disc."""
        for ruta, _ in ESTILS_PROJECTE:
            self.assertTrue(
                from_project_root(ruta).is_file(), f"falta el tema {ruta}"
            )

    def test_son_json_de_skylighting(self):
        """El JSON ha de tindre les claus que espera pandoc."""
        for ruta, _ in ESTILS_PROJECTE:
            tema = _tema(ruta)
            for clau in (
                "text-color",
                "background-color",
                "line-number-color",
                "line-number-background-color",
                "text-styles",
            ):
                self.assertIn(clau, tema, f"{ruta}: falta {clau}")
            for token, estil in tema["text-styles"].items():
                for clau in (
                    "text-color",
                    "background-color",
                    "bold",
                    "italic",
                    "underline",
                ):
                    self.assertIn(clau, estil, f"{ruta}/{token}: falta {clau}")

    def test_tots_els_tokens_tenen_color_llevat_de_normal(self):
        """Cap token pot quedar-se sense color (zenburn en deixava cinc).

        ``Normal`` és el text pla del bloc: ha d'heretar el color del ``<pre>``,
        no dur-ne un de propi.
        """
        for ruta, _ in ESTILS_PROJECTE:
            estils = _tema(ruta)["text-styles"]
            sense_color = {
                token for token, estil in estils.items()
                if estil["text-color"] is None
            }
            self.assertEqual(sense_color, {"Normal"}, f"{ruta}: {sense_color}")
            # La llista completa de skylighting (31 tokens).
            self.assertEqual(len(estils), 31, f"{ruta}: {len(estils)} tokens")

    def test_el_fons_coincidix_amb_el_del_bloc_de_codi(self):
        """El tema i el ``pre`` de base.css han de compartir el fons."""
        base_css = from_project_root("styles", "base.css").read_text(encoding="utf-8")
        self.assertIn(FONS, base_css.lower())
        for ruta, _ in ESTILS_PROJECTE:
            self.assertEqual(_tema(ruta)["background-color"].lower(), FONS, ruta)

    def test_cada_color_te_contrast_suficient(self):
        """Cada token ha de superar el contrast mínim sobre el fons fosc."""
        for ruta, _ in ESTILS_PROJECTE:
            tema = _tema(ruta)
            fons = tema["background-color"]
            for token, estil in tema["text-styles"].items():
                color = estil["text-color"]
                if color is None:
                    continue
                self.assertGreaterEqual(
                    _contrast(color, fons), CONTRAST_MINIM,
                    f"{ruta}: {token} {color} no arriba a {CONTRAST_MINIM}:1",
                )

    def test_la_puntuacio_es_neutra(self):
        """La puntuació no ha de dur color: ha de ser un gris.

        Pandoc no distingix parèntesis, comes i claus d'un operador: si eixe
        token va en cian, tot el bloc sembla ple d'operadors i costa llegir el
        codi (sobretot en Kotlin o Java, amb molts parèntesis).
        """
        for ruta, _ in ESTILS_PROJECTE:
            color = _tema(ruta)["text-styles"]["Operator"]["text-color"]
            canals = [int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
            saturacio = max(canals) - min(canals)
            self.assertLessEqual(
                saturacio, 40, f"{ruta}: Operator {color} no és un gris"
            )

    def test_les_variables_van_en_el_color_del_text(self):
        """Paràmetres i variables no han de dur color propi.

        En un editor els noms de variable es veuen com la resta del text; si
        van en roig (`Variable`), pareix que hi ha un error en cada línia.
        """
        for ruta, _ in ESTILS_PROJECTE:
            tema = _tema(ruta)
            self.assertEqual(
                tema["text-styles"]["Variable"]["text-color"].lower(),
                tema["text-color"].lower(),
                ruta,
            )

    @unittest.skipUnless(shutil.which("pandoc"), "cal pandoc al PATH")
    def test_pandoc_accepta_els_temes(self):
        """Pandoc ha de poder convertir amb cada tema sense error."""
        for ruta, _ in ESTILS_PROJECTE:
            resultat = subprocess.run(
                ["pandoc", "--highlight-style", str(from_project_root(ruta))],
                input="# Prova\n\n```kotlin\nval x = 1\n```\n",
                capture_output=True, text=True,
            )
            self.assertEqual(resultat.returncode, 0, f"{ruta}: {resultat.stderr}")



class TestRutaEstilRessaltat(unittest.TestCase):
    """Comprova la resolució del valor desat a la configuració."""

    def test_els_temes_de_pandoc_es_passen_tal_qual(self):
        """Un tema incorporat s'ha de passar pel nom, sense tocar-lo."""
        for estil in ESTILS_PANDOC:
            self.assertEqual(ruta_estil_ressaltat(estil), estil)

    def test_un_tema_de_pandoc_antic_es_respecta(self):
        """Una config vella amb ``tango`` ha de continuar funcionant."""
        self.assertEqual(ruta_estil_ressaltat("tango"), "tango")

    def test_un_tema_del_projecte_es_una_ruta_absoluta(self):
        """Els ``.theme`` s'han de passar a pandoc com a ruta absoluta."""
        for ruta, _ in ESTILS_PROJECTE:
            resolta = ruta_estil_ressaltat(ruta)
            self.assertTrue(resolta.startswith("/"), resolta)
            self.assertTrue(resolta.endswith(ruta), resolta)
            self.assertTrue(from_project_root(resolta).is_file(), resolta)

    def test_una_ruta_absoluta_tambe_val(self):
        """Si la configuració porta una ruta absoluta, s'ha de respectar."""
        absoluta = str(from_project_root(ESTILS_PROJECTE[1][0]).resolve())
        self.assertEqual(ruta_estil_ressaltat(absoluta), absoluta)

    def test_fitxer_inexistent_retorna_el_tema_per_defecte(self):
        """Un ``.theme`` esborrat no ha de trencar l'exportació."""
        with contextlib.redirect_stdout(io.StringIO()) as eixida:
            resolta = ruta_estil_ressaltat("themes/no-existeix.theme")
        self.assertEqual(
            resolta, str(from_project_root(ESTIL_RESSALTAT_DEFECTE).resolve())
        )
        self.assertIn("no-existeix.theme", eixida.getvalue())

    def test_valor_buit_retorna_el_tema_per_defecte(self):
        """Sense valor a la configuració s'usa el tema per defecte."""
        self.assertEqual(
            ruta_estil_ressaltat(""),
            str(from_project_root(ESTIL_RESSALTAT_DEFECTE).resolve()),
        )


class TestEstilsAlDesplegable(unittest.TestCase):
    """Comprova la llista d'estils que oferix el diàleg d'ajustos."""

    def test_el_primer_es_el_tema_per_defecte(self):
        """One Dark ha d'anar primer i ser el recomanat."""
        self.assertEqual(ESTILS_RESSALTAT[0], ESTILS_PROJECTE[0])
        self.assertEqual(ESTIL_RESSALTAT_DEFECTE, ESTILS_PROJECTE[0][0])
        self.assertIn("recomanat", ESTILS_RESSALTAT[0][1])

    def test_els_valors_son_unics(self):
        """No pot haver-hi dos temes amb el mateix valor desat."""
        valors = [estil for estil, _ in ESTILS_RESSALTAT]
        self.assertEqual(len(valors), len(set(valors)))

    def test_totes_les_etiquetes_avisen_que_el_tema_es_fosc(self):
        """Tots els temes oferits tenen fons fosc, com el bloc de codi."""
        for estil, etiqueta in ESTILS_RESSALTAT:
            self.assertIn("fosc", etiqueta, estil)

    def test_no_s_oferixen_temes_clars_de_pandoc(self):
        """Els temes clars de pandoc fan el codi quasi il·legible."""
        valors = {estil for estil, _ in ESTILS_RESSALTAT}
        self.assertEqual(
            valors & {"pygments", "tango", "kate", "haddock"}, set()
        )

    def test_el_default_es_un_tema_del_projecte(self):
        """La configuració per defecte apunta a un ``.theme`` existent."""
        self.assertIn(ESTIL_RESSALTAT_DEFECTE, [ruta for ruta, _ in ESTILS_PROJECTE])
        self.assertEqual(
            DEFAULT_CONFIG["highlight_style"], ESTIL_RESSALTAT_DEFECTE
        )


if __name__ == "__main__":
    unittest.main()
