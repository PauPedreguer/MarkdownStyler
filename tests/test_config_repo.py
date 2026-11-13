"""Tests unitaris per al repositori de configuració."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.core.identitats import PRESETS, es_color_valid
from src.infrastructure import config_repo
from src.infrastructure.highlight_styles import (
    ESTIL_RESSALTAT_DEFECTE,
    ESTILS_PROJECTE,
)
from src.infrastructure.project_paths import from_project_root


class TestConfigRepo(unittest.TestCase):
    """Comprova la càrrega i desat de la configuració."""

    def setUp(self):
        # Crear un directori temporal per aïllar els tests
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.config_file = self.tmp_path / "institut.json"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_load_returns_defaults_when_missing(self):
        """Si no existeix el fitxer, retorna la configuració per defecte."""
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()
        self.assertEqual(config["css_name"], "prova.css")
        self.assertEqual(config["template_name"], "base.html")
        self.assertEqual(config["js_name"], "script.js")
        self.assertEqual(config["highlight_style"], ESTIL_RESSALTAT_DEFECTE)
        # Mode presentació: valors per defecte encara que el JSON no els tinga.
        self.assertEqual(config["presentacio_nivell"], 2)
        self.assertEqual(config["presentacio_modus"], "diapositives")
        self.assertEqual(config["presentacio_tema"], "clar")

    def test_load_merges_with_defaults(self):
        """La configuració carregada es fusiona amb els valors per defecte."""
        self.config_file.write_text(
            json.dumps({"css_name": "custom.css", "institut_nom": "IES Test"}),
            encoding="utf-8",
        )
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()
        self.assertEqual(config["css_name"], "custom.css")
        self.assertEqual(config["institut_nom"], "IES Test")
        # Els valors no especificats mantenen el default
        self.assertEqual(config["template_name"], "base.html")

    def test_load_returns_defaults_on_invalid_json(self):
        """Si el JSON és invàlid, retorna els valors per defecte."""
        self.config_file.write_text("{invalid json", encoding="utf-8")
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()
        self.assertEqual(config["css_name"], "prova.css")

    def test_save_writes_file(self):
        """Desar la configuració ha de crear el fitxer JSON."""
        new_config = {"css_name": "nuevo.css", "institut_nom": "IES Nou"}
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config_repo.save_institut_config(new_config)
        self.assertTrue(self.config_file.exists())
        loaded = json.loads(self.config_file.read_text(encoding="utf-8"))
        self.assertEqual(loaded["css_name"], "nuevo.css")
        self.assertEqual(loaded["institut_nom"], "IES Nou")


class TestEstilRessaltatDelProjecte(unittest.TestCase):
    """El projecte ha de desar un tema de ressaltat propi i fosc.

    El bloc de codi té fons fosc (#1e293b): amb un tema clar (pygments, tango,
    kate, haddock) els tokens queden quasi negres sobre el fons i el codi
    sembla d'un sol color. Va passar de veritat: ``config/institut.json`` va
    quedar amb ``pygments`` i el ressaltat va desaparéixer.
    """

    def test_el_valor_per_defecte_es_un_tema_del_projecte(self):
        rutes = [ruta for ruta, _ in ESTILS_PROJECTE]
        self.assertIn(ESTIL_RESSALTAT_DEFECTE, rutes)
        self.assertEqual(config_repo.DEFAULT_CONFIG["highlight_style"],
                         ESTIL_RESSALTAT_DEFECTE)

    def test_el_tema_per_defecte_existeix_al_disc(self):
        self.assertTrue(from_project_root(ESTIL_RESSALTAT_DEFECTE).is_file())

    def test_la_config_del_projecte_es_un_tema_del_projecte(self):
        config = json.loads(
            from_project_root("config", "institut.json").read_text(encoding="utf-8")
        )
        self.assertIn(config["highlight_style"], [ruta for ruta, _ in ESTILS_PROJECTE])
        self.assertTrue(from_project_root(config["highlight_style"]).is_file())


class TestColorsDIdentitat(unittest.TestCase):
    """Comprova la llista de colors d'identitat de la configuració.

    Cada color del document porta un curs i una assignatura; si la clau no hi
    és (configuració antiga) s'han de generar els colors de sempre perquè la
    finestra principal sempre en tinga un de triat.
    """

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config_file = Path(self.tmp_dir.name) / "institut.json"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_genera_els_colors_si_la_clau_no_hi_es(self):
        """Una configuració sense `identitats` ha de rebre els presets."""
        self.config_file.write_text(
            json.dumps({"curs": "1r DAW", "assignatura": "LMSGI"}),
            encoding="utf-8",
        )
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()

        self.assertEqual(len(config["identitats"]), len(PRESETS))
        self.assertEqual(
            config["identitats"][0],
            {"color": "#1d4ed8", "curs": "1r DAW", "assignatura": "LMSGI"},
        )

    def test_normalitza_els_colors_del_fitxer(self):
        """Els colors desats es netegen (espais, caixa, camps que falten)."""
        self.config_file.write_text(
            json.dumps({"identitats": [
                {"color": " #166534 ", "curs": " 1r DAW ", "assignatura": "LMSGI"},
                "brossa",
            ]}),
            encoding="utf-8",
        )
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()

        self.assertEqual(
            config["identitats"],
            [{"color": "#166534", "curs": "1r DAW", "assignatura": "LMSGI"}],
        )

    def test_accepta_els_colors_escrits_pel_nom(self):
        """Al JSON també es pot escriure «Taronja» en compte del hexadecimal."""
        self.config_file.write_text(
            json.dumps({"identitats": [
                {"color": "Taronja", "curs": "1r DAW", "assignatura": "LMSGI"},
                {"color": "verd", "curs": "2n DAW", "assignatura": "DWEC"},
            ]}),
            encoding="utf-8",
        )
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()

        self.assertEqual(
            config["identitats"],
            [
                {"color": "#c2410c", "curs": "1r DAW", "assignatura": "LMSGI"},
                {"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"},
            ],
        )

    def test_descarta_les_entrades_que_no_son_diccionaris(self):
        """Cada color del JSON ha de ser un diccionari: el text s'ignora."""
        self.config_file.write_text(
            json.dumps({"identitats": [
                "Taronja - 1r DAW - LMSGI",
                {"color": "Verd", "curs": "2n DAW", "assignatura": "DWEC"},
            ]}),
            encoding="utf-8",
        )
        with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
            config = config_repo.load_institut_config()

        self.assertEqual(
            config["identitats"],
            [{"color": "#166534", "curs": "2n DAW", "assignatura": "DWEC"}],
        )

    def test_si_la_llista_es_buida_o_no_valida_es_regenera(self):
        """Una llista buida deixaria la finestra sense cap color triat."""
        for valor in ([], "text", None, [{"color": "no-es-un-color"}]):
            self.config_file.write_text(
                json.dumps({"identitats": valor}), encoding="utf-8"
            )
            with mock.patch.object(config_repo, "CONFIG_PATH", self.config_file):
                config = config_repo.load_institut_config()
            self.assertTrue(config["identitats"])
            self.assertTrue(es_color_valid(config["identitats"][0]["color"]))

    def test_la_config_del_projecte_porta_colors_amb_identitat(self):
        """El fitxer del projecte ha de dur la clau ja omplerta."""
        config = json.loads(
            from_project_root("config", "institut.json").read_text(encoding="utf-8")
        )
        identitats = config["identitats"]

        self.assertTrue(identitats)
        for identitat in identitats:
            self.assertTrue(es_color_valid(identitat["color"]), identitat)
        self.assertTrue(
            any(identitat["curs"] and identitat["assignatura"] for identitat in identitats)
        )

    def test_la_config_del_projecte_no_du_curs_ni_assignatura_a_dalt(self):
        """El curs i l'assignatura viuen només a la taula de colors."""
        config = json.loads(
            from_project_root("config", "institut.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("curs", config)
        self.assertNotIn("assignatura", config)


if __name__ == "__main__":
    unittest.main()
