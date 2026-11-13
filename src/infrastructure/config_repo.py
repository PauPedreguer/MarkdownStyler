import json
from pathlib import Path
from typing import Dict, Any
from src.core.identitats import normalitza_identitats, presets_per_defecte
from src.infrastructure.highlight_styles import ESTIL_RESSALTAT_DEFECTE
from src.infrastructure.project_paths import from_project_root

CONFIG_PATH = from_project_root("config", "institut.json")
DEFAULT_CONFIG: Dict[str, Any] = {
    "css_name": "prova.css",
    "template_name": "base.html",
    "js_name": "script.js",
    "highlight_style": ESTIL_RESSALTAT_DEFECTE,
    # Mode presentació (vegeu scripts/presentacio.js): el nivell de títol que
    # obri cada diapositiva, el mode inicial i el tema inicial del document.
    # El tema és únic per a la vista normal i la presentació: el botó ☾ (o la
    # tecla T) el canvia i el desa al navegador; este valor només s'aplica la
    # primera vegada, quan encara no hi ha preferència desada.
    "presentacio_nivell": 2,
    "presentacio_modus": "diapositives",
    "presentacio_tema": "clar",
}


def _amb_identitats(config: Dict[str, Any]) -> Dict[str, Any]:
    """Assegura que la configuració porta la llista de colors d'identitat.

    Les configuracions antigues no tenien la clau ``identitats`` (els colors
    estaven codificats a la finestra). En eixe cas es generen els colors de
    sempre; si la configuració encara duu el ``curs`` i l'``assignatura`` de
    dalt (claus que ara viuen només a la taula de colors), s'assignen al primer
    color, i així la finestra sempre té un color triat per defecte.

    Args:
        config: Configuració ja fusionada amb els valors per defecte.

    Returns:
        La mateixa configuració amb ``identitats`` sempre present i neta.
    """
    identitats = normalitza_identitats(config.get("identitats"))
    if not identitats:
        identitats = presets_per_defecte(
            config.get("curs", ""), config.get("assignatura", "")
        )
    config["identitats"] = identitats
    return config


def load_institut_config() -> Dict[str, Any]:
    """Carrega la configuració de l'institut des del fitxer JSON.

    Si el fitxer no existeix o és invàlid, retorna la configuració per defecte.
    Els valors carregats es fusionen amb els valors per defecte. La llista de
    colors d'identitat sempre arriba normalitzada i no buida.
    """
    try:
        if not CONFIG_PATH.parent.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not CONFIG_PATH.exists():
            return _amb_identitats(DEFAULT_CONFIG.copy())

        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return _amb_identitats({**DEFAULT_CONFIG, **loaded})
    except (FileNotFoundError, json.JSONDecodeError):
        return _amb_identitats(DEFAULT_CONFIG.copy())


def save_institut_config(config: Dict[str, Any]) -> None:
    """Desa la configuració de l'institut al fitxer JSON."""
    if not CONFIG_PATH.parent.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )

