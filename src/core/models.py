from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_dir: str
    title: str
    data: str
    subtitol: str = ""
    departament: str = "Informàtica"
    primary_color: str = "#1d4ed8"
    format: str = "html"
