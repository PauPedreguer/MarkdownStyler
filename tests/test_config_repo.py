"""Tests unitaris per al repositori de configuració."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.infrastructure import config_repo


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
        self.assertEqual(config["highlight_style"], "zenburn")

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


if __name__ == "__main__":
    unittest.main()
