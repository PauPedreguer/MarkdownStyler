from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_dir: str
    title: str
    curs_academic: str
    subtitol: str = ""
    # Buit → s'usa el departament de config/institut.json, que és on l'usuari
    # el configura (el formulari principal no el demana).
    departament: str = ""
    primary_color: str = "#1d4ed8"
    format: str = "html"
