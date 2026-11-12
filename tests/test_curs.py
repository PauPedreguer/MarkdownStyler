"""Tests del càlcul del curs acadèmic."""
import unittest
from datetime import datetime
from unittest import mock

from src.core import curs


class TestCursAcademic(unittest.TestCase):
    """Comprova el curs acadèmic segons el mes de l'any."""

    def _curs_amb_data(self, data):
        with mock.patch.object(curs, "datetime") as mock_datetime:
            mock_datetime.now.return_value = data
            return curs.calcular_curs_academic()

    def test_setembre_usa_l_any_actual_i_el_seguent(self):
        """A partir de setembre comença un curs nou."""
        self.assertEqual(self._curs_amb_data(datetime(2026, 9, 15)), "26-27")
        self.assertEqual(self._curs_amb_data(datetime(2026, 12, 31)), "26-27")

    def test_gener_a_agost_usa_l_any_anterior(self):
        """De gener a agost encara és el curs que va començar l'any anterior."""
        self.assertEqual(self._curs_amb_data(datetime(2027, 1, 1)), "26-27")
        self.assertEqual(self._curs_amb_data(datetime(2027, 8, 31)), "26-27")

    def test_els_anys_van_a_dos_digits(self):
        """El format ha de ser AA-AA amb dos dígits."""
        self.assertEqual(self._curs_amb_data(datetime(2100, 10, 1)), "00-01")


if __name__ == "__main__":
    unittest.main()
