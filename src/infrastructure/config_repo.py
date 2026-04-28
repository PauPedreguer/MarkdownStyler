import json
from pathlib import Path
from typing import Dict, Any
from src.infrastructure.project_paths import from_project_root

CONFIG_PATH = from_project_root("config", "institut.json")
DEFAULT_CONFIG: Dict[str, Any] = {
    "css_name": "prova.css",
    "template_name": "base.html",
    "js_name": "script.js",
    "highlight_style": "zenburn",
}

def load_institut_config() -> Dict[str, Any]:
    try:
        if not CONFIG_PATH.parent.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
        if not CONFIG_PATH.exists():
            return DEFAULT_CONFIG.copy()
            
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **loaded}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()

def save_institut_config(config: Dict[str, Any]) -> None:
    if not CONFIG_PATH.parent.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
