import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path("config/institut.json")

def load_institut_config() -> Dict[str, Any]:
    try:
        if not CONFIG_PATH.parent.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
        if not CONFIG_PATH.exists():
            return {}
            
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
