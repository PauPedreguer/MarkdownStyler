"""Tests unitaris dels colors d'identitat (color + curs + assignatura).

Cada color de la finestra principal va lligat a un curs i una assignatura que es
configuren a Configuració. Ací es comprova la lògica pura, sense PyQt6.
"""
import unittest

from src.core.identitats import (
    COLOR_PER_DEFECTE,
    PRESETS,
    color_per_nom,
    curs_i_assignatura,
    es_color_valid,
    etiqueta_identitat,
    identitat_efectiva,
    identitat_inicial,
    identitat_per_color,
    nom_curt_del_color,
    nom_del_color,
    normalitza_identitat,
    normalitza_identitats,
    presets_per_defecte,
)


class TestEsColorValid(unittest.TestCase):
    """Comprova la validació del color hexadecimal."""

    def test_accepta_hex_de_sis_digits(self):
        self.assertTrue(es_color_valid("#1d4ed8"))
        self.assertTrue(es_color_valid("#FFFFFF"))
        self.assertTrue(es_color_valid("  #0f766e  "))

    def test_rebutja_altres_formats(self):
        for valor in ("#fff", "1d4ed8", "blau", "", None, 123, "#12345g"):
            self.assertFalse(es_color_valid(valor), valor)


class TestNormalitzaIdentitat(unittest.TestCase):
    """Comprova la neteja d'una identitat vinguda del JSON o del diàleg."""

    def test_lleva_espais_i_normalitza_el_color(self):
        identitat = normalitza_identitat(
            {"color": " #1D4ED8 ", "curs": " 1r DAW ", "assignatura": "LMSGI "}
        )
        self.assertEqual(
            identitat,
            {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
        )

    def test_accepta_el_color_pel_nom(self):
        """Al JSON es pot escriure el color pel nom: «Taronja»."""
        self.assertEqual(
            normalitza_identitat({"color": "Taronja", "curs": "1r DAW"}),
            {"color": "#c2410c", "curs": "1r DAW", "assignatura": ""},
        )

    def test_usa_el_color_per_defecte_si_no_es_valid(self):
        self.assertEqual(
            normalitza_identitat({"color": "blauet"})["color"], COLOR_PER_DEFECTE
        )

    def test_admet_valors_buits_o_incorrectes(self):
        expected = {"color": COLOR_PER_DEFECTE, "curs": "", "assignatura": ""}
        self.assertEqual(normalitza_identitat(None), expected)
        self.assertEqual(normalitza_identitat("text"), expected)
        self.assertEqual(normalitza_identitat({}), expected)


class TestNormalitzaIdentitats(unittest.TestCase):
    """Comprova la neteja de la llista sencera de colors."""

    def test_descarta_entrades_que_no_son_diccionaris(self):
        netes = normalitza_identitats(["text", 3, None, {"color": "#166534"}])
        self.assertEqual(len(netes), 1)
        self.assertEqual(netes[0]["color"], "#166534")

    def test_accepta_entrades_amb_el_color_pel_nom(self):
        """Al JSON es pot escriure el color pel nom: «Taronja»."""
        netes = normalitza_identitats(
            [
                {"color": "Taronja", "curs": "1r DAW", "assignatura": "LMSGI"},
                {"color": "Verd", "curs": "2n DAW", "assignatura": "DWEC"},
            ]
        )
        self.assertEqual(
            netes,
            [
                {"color": "#c2410c", "curs": "1r DAW", "assignatura": "LMSGI"},
                {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
            ],
        )

    def test_lleva_els_duplicats_exactes(self):
        duplicada = {"color": "#166534", "curs": "1r DAW", "assignatura": "LMSGI"}
        netes = normalitza_identitats([duplicada, dict(duplicada)])
        self.assertEqual(len(netes), 1)

    def test_conserva_el_mateix_color_amb_assignatures_diferents(self):
        netes = normalitza_identitats([
            {"color": "#166534", "curs": "1r DAW", "assignatura": "LMSGI"},
            {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
        ])
        self.assertEqual(len(netes), 2)

    def test_retorna_llista_buida_si_no_es_una_llista(self):
        for valor in (None, "text", {}, 5):
            self.assertEqual(normalitza_identitats(valor), [])


class TestPresetsPerDefecte(unittest.TestCase):
    """Comprova els colors que es generen quan la configuració no en té."""

    def test_genera_un_color_per_cada_preset(self):
        identitats = presets_per_defecte()
        self.assertEqual(len(identitats), len(PRESETS))
        self.assertEqual(
            [identitat["color"] for identitat in identitats],
            [color for color, _ in PRESETS],
        )

    def test_nomes_el_primer_porta_curs_i_assignatura(self):
        identitats = presets_per_defecte("1r DAW", "LMSGI")
        self.assertEqual(curs_i_assignatura(identitats[0]), ("1r DAW", "LMSGI"))
        for identitat in identitats[1:]:
            self.assertEqual(curs_i_assignatura(identitat), ("", ""))


class TestNomDelColor(unittest.TestCase):
    """Comprova el nom humà dels colors coneguts."""

    def test_retorna_el_nom_del_preset(self):
        self.assertEqual(nom_del_color("#1d4ed8"), "Blau")
        self.assertEqual(nom_del_color("#1D4ED8"), "Blau")

    def test_d_un_color_desconegut_retorna_el_hex(self):
        self.assertEqual(nom_del_color("#9f1239"), "#9F1239")


class TestEtiquetaIdentitat(unittest.TestCase):
    """Comprova l'etiqueta que es veu davall del color."""

    def test_ajunta_curs_i_assignatura(self):
        self.assertEqual(
            etiqueta_identitat({"curs": "1r DAW", "assignatura": "LMSGI"}),
            "1r DAW · LMSGI",
        )

    def test_amb_nomes_una_dada_no_deixa_separador(self):
        self.assertEqual(etiqueta_identitat({"assignatura": "LMSGI"}), "LMSGI")
        self.assertEqual(etiqueta_identitat({"curs": "1r DAW"}), "1r DAW")

    def test_sense_dades_retorna_el_nom_del_color(self):
        self.assertEqual(
            etiqueta_identitat({"color": "#166534", "curs": "", "assignatura": ""}),
            "Verd",
        )


class TestIdentitatPerColor(unittest.TestCase):
    """Comprova la busca d'una identitat pel seu color."""

    def setUp(self):
        self.identitats = presets_per_defecte("1r DAW", "LMSGI")

    def test_troba_el_color_sense_distingir_majuscules(self):
        trobada = identitat_per_color(self.identitats, "#1D4ED8")
        self.assertEqual(curs_i_assignatura(trobada), ("1r DAW", "LMSGI"))

    def test_retorna_none_si_no_hi_es(self):
        self.assertIsNone(identitat_per_color(self.identitats, "#9f1239"))


class TestIdentitatInicial(unittest.TestCase):
    """Comprova quin color apareix triat en obrir la finestra."""

    def test_usa_el_primer_color_de_la_configuracio(self):
        identitats = [
            {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
            {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
        ]
        triada = identitat_inicial(identitats)
        self.assertEqual(triada["color"], "#166534")
        self.assertEqual(curs_i_assignatura(triada), ("2n DAW", "DWEC"))

    def test_sense_identitats_retorna_el_color_per_defecte(self):
        triada = identitat_inicial([])
        self.assertEqual(
            triada,
            {"color": COLOR_PER_DEFECTE, "curs": "", "assignatura": ""},
        )

class TestIdentitatEfectiva(unittest.TestCase):
    """Comprova quina identitat acaba tenint el color triat."""

    def setUp(self):
        self.identitats = [
            {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
            {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
            {"color": "#c2410c", "curs": "", "assignatura": ""},
        ]

    def test_el_color_triat_mane_amb_la_seua_identitat(self):
        triada = identitat_efectiva(self.identitats, "#166534")
        self.assertEqual(triada["color"], "#166534")
        self.assertEqual(curs_i_assignatura(triada), ("2n DAW", "DWEC"))

    def test_el_color_sense_dades_agafa_les_del_document_per_defecte(self):
        triada = identitat_efectiva(self.identitats, "#c2410c")
        self.assertEqual(triada["color"], "#c2410c")
        self.assertEqual(curs_i_assignatura(triada), ("1r DAW", "LMSGI"))

    def test_un_color_desconegut_es_el_document_per_defecte(self):
        self.assertEqual(
            identitat_efectiva(self.identitats, "#9f1239"),
            {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
        )

    def test_sense_identitats_retorna_el_color_per_defecte(self):
        self.assertEqual(
            identitat_efectiva([], "#9f1239"),
            {"color": COLOR_PER_DEFECTE, "curs": "", "assignatura": ""},
        )


class TestColorPerNom(unittest.TestCase):
    """Comprova la conversió d'un nom de color al hexadecimal."""

    def test_accepta_els_noms_curts_sense_accent_ni_majuscules(self):
        self.assertEqual(color_per_nom("Taronja"), "#c2410c")
        self.assertEqual(color_per_nom("  BLAU  "), "#1d4ed8")
        self.assertEqual(color_per_nom("marro"), "#78350f")
        self.assertEqual(color_per_nom("Marró"), "#78350f")

    def test_accepta_les_etiquetes_dels_presets(self):
        self.assertEqual(color_per_nom("Blau"), "#1d4ed8")
        self.assertEqual(color_per_nom("verd"), "#166534")
        self.assertEqual(color_per_nom("Groc"), "#d4ac00")

    def test_els_noms_dels_presets_son_curts_i_coherents(self):
        """Cada preset es pot escriure pel seu nom i eixe nom és curt."""
        for color, nom in PRESETS:
            self.assertNotIn(" ", nom)
            self.assertEqual(color_per_nom(nom), color)
            self.assertEqual(nom_del_color(color), nom)

    def test_accepta_un_hexadecimal_i_el_normalitza(self):
        self.assertEqual(color_per_nom("#C2410C"), "#c2410c")

    def test_si_no_es_reconeix_retorna_none(self):
        for valor in ("verd clar", "", None, "#12345", 42):
            self.assertIsNone(color_per_nom(valor), valor)


class TestNomCurtDelColor(unittest.TestCase):
    """Comprova el nom curt amb què s'escriuen els colors a Configuració."""

    def test_retorna_el_nom_curt_del_color(self):
        self.assertEqual(nom_curt_del_color("#c2410c"), "Taronja")
        self.assertEqual(nom_curt_del_color("#1D4ED8"), "Blau")

    def test_d_un_color_sense_nom_retorna_el_hex(self):
        self.assertEqual(nom_curt_del_color("#9f1239"), "#9F1239")


if __name__ == "__main__":
    unittest.main()
