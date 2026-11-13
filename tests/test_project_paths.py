"""Tests unitaris per a les rutes del projecte."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.infrastructure import project_paths
from src.infrastructure.project_paths import (
    DATA_ROOT,
    PROJECT_ROOT,
    RESOURCE_ROOT,
    directoris_de_recurs,
    from_data_root,
    from_project_root,
    recurs,
)


class TestProjectPaths(unittest.TestCase):
    """Comprova la resolució de rutes del projecte."""

    def test_project_root_is_absolute(self):
        """PROJECT_ROOT ha de ser una ruta absoluta."""
        self.assertTrue(PROJECT_ROOT.is_absolute())

    def test_project_root_points_to_project(self):
        """PROJECT_ROOT ha d'apuntar a l'arrel del projecte."""
        # L'arrel del projecte conté main.py i src/
        self.assertTrue((PROJECT_ROOT / "main.py").exists())
        self.assertTrue((PROJECT_ROOT / "src").is_dir())

    def test_from_project_root_joins_parts(self):
        """from_project_root ha de concatenar les parts correctament."""
        path = from_project_root("src", "core", "models.py")
        self.assertEqual(path, PROJECT_ROOT / "src" / "core" / "models.py")
        self.assertTrue(path.exists())

    def test_from_project_root_single_part(self):
        """from_project_root amb un sol argument."""
        path = from_project_root("config")
        self.assertEqual(path, PROJECT_ROOT / "config")

    def test_resource_root_es_project_root(self):
        """En desenvolupament els recursos són l'arbre del projecte."""
        self.assertEqual(RESOURCE_ROOT, PROJECT_ROOT)


class TestArbreDeDades(unittest.TestCase):
    """Comprova que les dades d'usuari queden fora del paquet.

    Els paquets (.deb, .rpm, AppImage, .exe) són de només lectura: la
    configuració i els recursos importats no poden viure dins dels recursos.
    """

    def test_data_root_es_absolut_i_fora_dels_recursos(self):
        self.assertTrue(DATA_ROOT.is_absolute())
        self.assertNotEqual(DATA_ROOT, RESOURCE_ROOT)

    def test_from_data_root_joins_parts(self):
        self.assertEqual(
            from_data_root("config", "institut.json"),
            DATA_ROOT / "config" / "institut.json",
        )

    def test_la_variable_d_entorn_canvia_l_arrel_de_dades(self):
        """MARKDOWN_STYLER_DATA servix per al mode portable i per als tests."""
        with mock.patch.dict(os.environ, {project_paths.VARIABLE_DADES: "/tmp/ms-data"}):
            self.assertEqual(
                project_paths._calcula_arrel_dades(), Path("/tmp/ms-data")
            )

    def test_directoris_de_recurs_dona_primer_el_de_l_usuari(self):
        directoris = directoris_de_recurs("styles")
        self.assertEqual(directoris[0], DATA_ROOT / "styles")
        self.assertEqual(directoris[1], RESOURCE_ROOT / "styles")


class TestRecurs(unittest.TestCase):
    """Comprova la prioritat entre el recurs de l'usuari i el del paquet."""

    def test_sense_copia_de_l_usuari_guanya_el_paquet(self):
        self.assertEqual(
            recurs("styles", "base.css"),
            RESOURCE_ROOT / "styles" / "base.css",
        )
        self.assertTrue(recurs("styles", "base.css").is_file())

    def test_amb_copia_de_l_usuari_guanya_la_de_l_usuari(self):
        with tempfile.TemporaryDirectory() as tmp:
            estil = Path(tmp) / "styles" / "base.css"
            estil.parent.mkdir()
            estil.write_text("/* */", encoding="utf-8")
            with mock.patch.object(project_paths, "DATA_ROOT", Path(tmp)):
                self.assertEqual(recurs("styles", "base.css"), estil)


if __name__ == "__main__":
    unittest.main()
