from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Icona del botó i del diàleg de configuració. És un SVG propi perquè l'emoji
# (⚙️) es veu diferent a cada sistema i en alguns ni s'arriba a pintar. La
# variant blanca és per als botons blaus, on la blava no es veuria.
ICONA_CONFIGURACIO = ("assets", "icones", "configuracio.svg")
ICONA_CONFIGURACIO_BLANCA = ("assets", "icones", "configuracio-blanc.svg")


def from_project_root(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def icona_configuracio(blanca: bool = False) -> Path:
    """Retorna la ruta de la icona de configuració de l'aplicació.

    Args:
        blanca: ``True`` per a la variant blanca, la que es veu damunt dels
            botons blaus de la interfície.

    Returns:
        La ruta del fitxer SVG.
    """
    parts = ICONA_CONFIGURACIO_BLANCA if blanca else ICONA_CONFIGURACIO
    return from_project_root(*parts)

