"""Càlcul del curs acadèmic actual.

Es manté fora de la interfície perquè també el fa servir el mode de línia
d'ordres (``main.py --pdf``), que no ha de carregar PyQt6.
"""
from datetime import datetime


def calcular_curs_academic() -> str:
    """Calcula el curs acadèmic actual (ex: '26-27').

    Entre setembre i desembre → any actual + següent (ex: oct 2026 → '26-27').
    Entre gener i agost → any anterior + actual (ex: març 2027 → '26-27').

    Returns:
        El curs acadèmic en format ``AA-AA``.
    """
    now = datetime.now()
    any_ini = now.year if now.month >= 9 else now.year - 1
    any_fi = any_ini + 1
    return f"{any_ini % 100:02d}-{any_fi % 100:02d}"
