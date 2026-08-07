"""Tests unitaris per a les rutes del projecte."""
import unittest
from pathlib import Path

from src.infrastructure.project_paths import PROJECT_ROOT, from_project_root


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


if __name__ == "__main__":
    unittest.main()
