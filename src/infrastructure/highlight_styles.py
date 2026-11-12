"""Estils de ressaltat de codi (--highlight-style) que pot usar Pandoc.

Pandoc admet dos tipus de valor a ``--highlight-style``:

- el **nom** d'un dels temes que porta incorporats (``zenburn``, ``espresso``…);
- la **ruta** d'un fitxer ``.theme`` amb el format JSON de skylighting.

Els temes propis del projecte viuen a ``themes/`` i estan afinats per al fons
fosc del bloc de codi (``#1e293b``, el de ``styles/base.css``) i per als
llenguatges que s'usen a classe: kotlin, java, bash, html, css, javascript,
c++, c# i php. Els temes de pandoc de fons clar (``pygments``, ``tango``,
``kate``, ``haddock``) no s'oferixen: sobre el fons fosc deixen els tokens
quasi negres i el codi sembla d'un sol color.
"""
from src.infrastructure.project_paths import from_project_root

# Temes incorporats a pandoc que es llegixen bé sobre el fons fosc.
ESTILS_PANDOC = ("zenburn", "espresso", "breezedark", "monochrome")

# Temes propis: (valor desat a la configuració, etiqueta visible al desplegable).
ESTILS_PROJECTE = (
    ("themes/one-dark.theme", "One Dark — fosc (recomanat)"),
    ("themes/material-ocean.theme", "Material Ocean — fosc"),
    ("themes/github-dark.theme", "GitHub Dark — fosc"),
)

# Estil que s'usa si la configuració no en diu cap o apunta a un fitxer perdut.
ESTIL_RESSALTAT_DEFECTE = ESTILS_PROJECTE[0][0]

# Etiqueta de cada tema incorporat de pandoc.
ETIQUETES_PANDOC = {
    "zenburn": "zenburn — fosc (de pandoc)",
    "espresso": "espresso — fosc (de pandoc)",
    "breezedark": "breezedark — fosc, poc contrast (de pandoc)",
    "monochrome": "monochrome — fosc sense colors (de pandoc)",
}

# Totes les opcions del desplegable d'ajustos: primer els temes propis.
ESTILS_RESSALTAT = ESTILS_PROJECTE + tuple(
    (estil, ETIQUETES_PANDOC[estil]) for estil in ESTILS_PANDOC
)


def ruta_estil_ressaltat(valor: str) -> str:
    """Resol el valor de ``--highlight-style`` a partir de la configuració.

    Args:
        valor: Nom d'un tema de pandoc (``"zenburn"``, ``"tango"``…) o ruta
            (relativa al projecte o absoluta) d'un fitxer ``.theme``, per
            exemple ``"themes/one-dark.theme"``.

    Returns:
        El nom del tema si és un tema incorporat de pandoc, o la ruta absoluta
        del fitxer ``.theme``. Si el fitxer no existeix, avisa per stdout i
        retorna el tema per defecte: així un ``.theme`` esborrat no trenca
        l'exportació del document.
    """
    # Un valor sense separadors de ruta és un tema incorporat de pandoc
    # (zenburn, espresso, tango…): es passa pel nom, tal com va arribar.
    if valor and "/" not in valor and not valor.endswith(".theme"):
        return valor

    defecte = from_project_root(ESTIL_RESSALTAT_DEFECTE)
    ruta = from_project_root(valor) if valor else defecte
    if ruta.is_file():
        return str(ruta.resolve())

    if valor:
        print(
            f"Avís: no s'ha trobat l'estil de ressaltat '{valor}'; "
            f"s'usa '{ESTIL_RESSALTAT_DEFECTE}'."
        )
    if defecte.is_file():
        return str(defecte.resolve())
    # Últim recurs: el tema que sempre porta pandoc.
    return "zenburn"
