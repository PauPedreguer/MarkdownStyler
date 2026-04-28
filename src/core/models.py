from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_dir: str
    title: str
    data: str
    primary_color: str = "#1d4ed8"
