"""Rutes de l'aplicació: recursos del paquet i dades de l'usuari.

L'aplicació es pot executar de tres maneres, i cadascuna deixa els fitxers en
un lloc distint:

- **Des del codi font**, amb l'arrel del projecte com a recursos.
- **Empaquetada amb PyInstaller** (AppImage, Windows): els recursos es
  desempaqueten a ``sys._MEIPASS``, que és de només lectura (a l'AppImage,
  dins d'una imatge squashfs muntada de només lectura).
- **Instal·lada des d'un .deb/.rpm**: els recursos viuen a
  ``/usr/lib/markdown-styler``, també de només lectura per a l'usuari.

Per això es distingixen dos arbres:

``RESOURCE_ROOT``
    Estils, plantilles, scripts, temes i icones que viatgen amb l'aplicació.
    Mai no s'hi escriu: si l'usuari importa un CSS, va a ``DATA_ROOT``.

``DATA_ROOT``
    Configuració de l'institut i recursos importats per l'usuari. És
    ``~/.local/share/MarkdownStyler`` (XDG) a Linux i
    ``%APPDATA%/MarkdownStyler`` a Windows. La variable d'entorn
    ``MARKDOWN_STYLER_DATA`` el pot canviar (mode portable i tests).
"""
import os
import sys
from pathlib import Path

NOM_APLICACIO = "MarkdownStyler"

# Variable d'entorn per a canviar el directori de dades (mode portable).
VARIABLE_DADES = "MARKDOWN_STYLER_DATA"


def _calcula_arrel_recursos() -> Path:
    """Calcula l'arrel dels recursos que viatgen amb l'aplicació."""
    if getattr(sys, "frozen", False):
        # PyInstaller definix _MEIPASS tant en mode onefile com en onedir.
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent.parent


def _calcula_arrel_dades() -> Path:
    """Calcula l'arrel de les dades de l'usuari (escriptura)."""
    canviada = os.environ.get(VARIABLE_DADES)
    if canviada:
        return Path(canviada).expanduser()

    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser(
            "~/.local/share"
        )
    return Path(base).expanduser() / NOM_APLICACIO


# Arbre de només lectura: tot el que viatja amb el paquet.
RESOURCE_ROOT = _calcula_arrel_recursos()
# Arbre d'escriptura: configuració i recursos importats per l'usuari.
DATA_ROOT = _calcula_arrel_dades()

# Nom antic de RESOURCE_ROOT: el codi i els tests encara el fan servir.
PROJECT_ROOT = RESOURCE_ROOT

# Icona del botó i del diàleg de configuració. És un SVG propi perquè l'emoji
# (⚙️) es veu diferent a cada sistema i en alguns ni s'arriba a pintar. La
# variant blanca és per als botons blaus, on la blava no es veuria.
ICONA_CONFIGURACIO = ("assets", "icones", "configuracio.svg")
ICONA_CONFIGURACIO_BLANCA = ("assets", "icones", "configuracio-blanc.svg")


def from_project_root(*parts: str) -> Path:
    """Ruta dins dels recursos de l'aplicació (només lectura)."""
    return RESOURCE_ROOT.joinpath(*parts)


def from_data_root(*parts: str) -> Path:
    """Ruta dins de les dades de l'usuari (escriptura)."""
    return DATA_ROOT.joinpath(*parts)


def recurs(*parts: str) -> Path:
    """Resol un recurs: primer la còpia de l'usuari, després la del paquet.

    Els recursos importats des del diàleg de configuració es desen a
    ``DATA_ROOT``; els que viatgen amb l'aplicació, a ``RESOURCE_ROOT``. Quan
    n'hi ha dos amb el mateix nom mana el de l'usuari, perquè és el que acaba
    de triar.

    Args:
        *parts: Camí relatiu del recurs, per exemple ``("styles", "meu.css")``.

    Returns:
        La ruta del recurs de l'usuari si existix; si no, la del paquet.
    """
    relativa = Path(*parts)
    de_usuari = DATA_ROOT / relativa
    if de_usuari.exists():
        return de_usuari
    return RESOURCE_ROOT / relativa


def directoris_de_recurs(*parts: str) -> tuple:
    """Directoris on buscar un tipus de recurs, per orde de prioritat.

    Args:
        *parts: Camí relatiu del directori, per exemple ``("styles",)``.

    Returns:
        Una tupla amb el directori de l'usuari i el del paquet.
    """
    relativa = Path(*parts)
    return (DATA_ROOT / relativa, RESOURCE_ROOT / relativa)


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
