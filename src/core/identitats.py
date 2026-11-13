"""Colors d'identitat: cada color va lligat a un curs i una assignatura.

La finestra principal mostra un color per cada parella curs/assignatura i, en
triar-ne un, el document n'hereta el color i les dades de la capçalera (i de la
portada del PDF). El mapa es desa a ``config/institut.json`` (clau
``identitats``, una llista de ``{"color", "curs", "assignatura"}``) i s'edita
des de la taula de la configuració.

El color pot ser un nom (``Taronja``, ``Verd``...) o un hexadecimal
(``#c2410c``); el curs i l'assignatura són opcionals. El primer color de la
llista és el document per defecte: és el que apareix triat en obrir la finestra
i el que s'usa si el color triat no porta curs o assignatura.

Es manté fora de la interfície (com ``curs.py``) perquè la lògica es puga
provar sense PyQt6 i perquè també la puga usar el mode de línia d'ordres.
"""
import re
import unicodedata

# Color d'identitat per defecte (Blau).
COLOR_PER_DEFECTE = "#1d4ed8"

# Els colors que la finestra duia codificats abans de poder-los editar. Servixen
# per a generar la configuració inicial i per a tindre un nom humà per al
# tooltip; l'usuari pot esborrar-los tots llevat d'un.
PRESETS: tuple[tuple[str, str], ...] = (
    ("#1d4ed8", "Blau"),
    ("#166534", "Verd"),
    ("#334155", "Gris"),
    ("#dc2626", "Roig"),
    ("#c2410c", "Taronja"),
    ("#6b21a8", "Lila"),
    ("#0891b2", "Turquesa"),
    ("#d4ac00", "Groc"),
)

# Colors que es poden escriure pel nom al camp de color de la taula (i al JSON).
# L'orde és el que es mostra a l'ajuda del diàleg.
COLORS_AMB_NOM: dict[str, str] = {
    "blau": "#1d4ed8",
    "verd": "#166534",
    "taronja": "#c2410c",
    "gris": "#334155",
    "granat": "#991b1b",
    "ocre": "#b45309",
    "lila": "#6b21a8",
    "teal": "#0f766e",
    "groc": "#d4ac00",
    "roig": "#dc2626",
    "rosa": "#db2777",
    "turquesa": "#0891b2",
    "marró": "#78350f",
    "negre": "#111827",
}

_NOMS = {color: nom for color, nom in PRESETS}
_NOMS_SIMPLES = {color: nom.capitalize() for nom, color in COLORS_AMB_NOM.items()}
_RE_HEX = re.compile(r"^#[0-9a-f]{6}$", re.IGNORECASE)


def _text(valor: object) -> str:
    """Retorna un valor com a text net (mai ``None`` ni ``"None"``)."""
    return "" if valor is None else str(valor).strip()


def _sense_accents(text: str) -> str:
    """Retorna el text sense accents, per a comparar noms de color."""
    descompost = unicodedata.normalize("NFKD", text)
    return "".join(lletra for lletra in descompost if not unicodedata.combining(lletra))


def _clau_nom(text: object) -> str:
    """Retorna la clau amb què es busca un nom de color (sense accents)."""
    return re.sub(r"\s+", " ", _sense_accents(_text(text)).lower())


# Noms acceptats: els curts («taronja») i les etiquetes dels presets
# («blau professional»). Les claus ja van normalitzades.
_ALIASOS: dict[str, str] = {
    **{_clau_nom(nom): color for nom, color in COLORS_AMB_NOM.items()},
    **{_clau_nom(nom): color for color, nom in PRESETS},
}


def es_color_valid(valor: object) -> bool:
    """Comprova que un valor és un color hexadecimal ``#rrggbb``.

    Args:
        valor: Valor a validar (normalment el ``color`` d'una identitat).

    Returns:
        ``True`` si és un text amb la forma ``#rrggbb`` (en qualsevol caixa).
    """
    return isinstance(valor, str) and bool(_RE_HEX.match(valor.strip()))


def color_per_nom(valor: object) -> str | None:
    """Convertix un nom de color (o un hexadecimal) en el color hexagonal.

    Args:
        valor: Nom del color (``Taronja``, ``blau professional``...) o un color
            hexadecimal (``#c2410c``).

    Returns:
        El color en minúscules (``#c2410c``), o ``None`` si no es reconeix.
    """
    text = _text(valor)
    if es_color_valid(text):
        return text.lower()
    return _ALIASOS.get(_clau_nom(text))


def normalitza_identitat(valor: object) -> dict:
    """Retorna una identitat amb les tres claus com a text net.

    Args:
        valor: Diccionari amb ``color``, ``curs`` i ``assignatura`` (pot faltar
            qualsevol de les tres claus, o no ser ni un diccionari).

    Returns:
        Un diccionari nou amb el ``color`` en minúscules (``#1d4ed8``), el
        ``curs`` i l'``assignatura`` sense espais sobrants. El ``color`` pot
        vindre com a hexadecimal o pel nom (``Taronja``); si no es reconeix
        s'usa ``COLOR_PER_DEFECTE``.
    """
    dades = valor if isinstance(valor, dict) else {}
    color = _text(dades.get("color")).lower()
    return {
        "color": color_per_nom(color) or COLOR_PER_DEFECTE,
        "curs": _text(dades.get("curs")),
        "assignatura": _text(dades.get("assignatura")),
    }


def normalitza_identitats(valors: object) -> list[dict]:
    """Netja una llista de colors d'identitat que ve del JSON.

    Cada entrada ha de ser un diccionari amb ``color`` (obligatori) i,
    opcionalment, ``curs`` i ``assignatura``; la resta d'entrades es descarten.
    Es validen els colors i es lleven els duplicats exactes (mateix color, curs
    i assignatura) conservant l'orde.

    Args:
        valors: Valor llegit de la configuració (pot no ser una llista).

    Returns:
        La llista d'identitats netes; buida si ``valors`` no és una llista.
    """
    if not isinstance(valors, (list, tuple)):
        return []

    netes: list[dict] = []
    vistes: set[tuple[str, str, str]] = set()
    for valor in valors:
        if not isinstance(valor, dict):
            continue
        identitat = normalitza_identitat(valor)
        clau = (identitat["color"], identitat["curs"], identitat["assignatura"])
        if clau in vistes:
            continue
        vistes.add(clau)
        netes.append(identitat)
    return netes


def presets_per_defecte(curs: str = "", assignatura: str = "") -> list[dict]:
    """Genera la llista de colors inicial (els que duia la finestra).

    Args:
        curs: Curs que s'assigna al primer color (el document per defecte).
        assignatura: Assignatura que s'assigna al primer color.

    Returns:
        Una identitat per cada ``PRESETS``; només la primera porta curs i
        assignatura, la resta queden sense assignar perquè l'usuari les omplisca.
    """
    return [
        {
            "color": color,
            "curs": _text(curs) if index == 0 else "",
            "assignatura": _text(assignatura) if index == 0 else "",
        }
        for index, (color, _) in enumerate(PRESETS)
    ]


def nom_curt_del_color(color: str) -> str:
    """Retorna el nom curt (català) d'un color, si en té.

    Args:
        color: Color hexadecimal.

    Returns:
        ``Taronja``, ``Verd``... si el color és dels que tenen nom; si no, el
        mateix color en majúscules.
    """
    net = _text(color).lower()
    if net in _NOMS_SIMPLES:
        return _NOMS_SIMPLES[net]
    return _text(color).upper() or COLOR_PER_DEFECTE.upper()


def nom_del_color(color: str) -> str:
    """Retorna el nom humà d'un color.

    Args:
        color: Color hexadecimal.

    Returns:
        El nom del preset (``Blau``), el nom curt (``Taronja``) o
        el mateix color en majúscules si no és cap dels coneguts.
    """
    net = _text(color)
    return _NOMS.get(net.lower()) or nom_curt_del_color(net)


def etiqueta_identitat(identitat: dict) -> str:
    """Retorna l'etiqueta que es veu davall del color.

    Args:
        identitat: Diccionari amb ``color``, ``curs`` i ``assignatura``.

    Returns:
        ``"1r DAW · LMSGI"``, el nom del color si no té cap de les dos dades,
        o el mateix color si tampoc no en té nom.
    """
    curs = _text(identitat.get("curs"))
    assignatura = _text(identitat.get("assignatura"))
    parts = [part for part in (curs, assignatura) if part]
    if parts:
        return " · ".join(parts)
    return nom_del_color(identitat.get("color", COLOR_PER_DEFECTE))


def curs_i_assignatura(identitat: dict) -> tuple[str, str]:
    """Retorna el curs i l'assignatura d'una identitat com a text net."""
    return _text(identitat.get("curs")), _text(identitat.get("assignatura"))


def identitat_per_color(identitats: list[dict], color: str) -> dict | None:
    """Busca la identitat que té eixe color.

    Args:
        identitats: Llista d'identitats ja normalitzada.
        color: Color hexadecimal a buscar (no distingix majúscules).

    Returns:
        La primera identitat amb eixe color, o ``None`` si no n'hi ha cap.
    """
    buscat = _text(color).lower()
    for identitat in identitats:
        if _text(identitat.get("color")).lower() == buscat:
            return identitat
    return None


def identitat_inicial(identitats: list[dict]) -> dict:
    """Retorna el color que ha d'aparéixer triat en obrir la finestra.

    El primer color de la llista és el document per defecte: ix triat en obrir
    la finestra i és el que s'usa si el color triat no porta curs ni
    assignatura.

    Args:
        identitats: Llista d'identitats (es normalitza abans de mirar-la).

    Returns:
        La primera identitat; si no n'hi ha cap de vàlida, la del color per
        defecte sense curs ni assignatura.
    """
    netes = normalitza_identitats(identitats)
    if not netes:
        return {"color": COLOR_PER_DEFECTE, "curs": "", "assignatura": ""}
    return netes[0]


def identitat_efectiva(identitats: list[dict], color: str) -> dict:
    """Retorna la identitat que acaba tenint el document.

    El color triat a la finestra pot no portar curs ni assignatura; en eixe cas
    el document agafa els del color per defecte (la primera identitat), que és
    el mateix criteri que aplica la generació de l'HTML.

    Args:
        identitats: Llista d'identitats (es normalitza abans de buscar-hi).
        color: Color hexadecimal del botó triat a la finestra.

    Returns:
        La identitat del color triat amb el curs i l'assignatura que li
        corresponen: els seus o, si en falten, els del document per defecte.
        Si el color no és a la llista, torna el document per defecte.
    """
    triada = identitat_per_color(normalitza_identitats(identitats), color)
    defecte = identitat_inicial(identitats)
    if triada is None:
        return defecte
    return {
        "color": triada["color"],
        "curs": triada["curs"] or defecte["curs"],
        "assignatura": triada["assignatura"] or defecte["assignatura"],
    }
