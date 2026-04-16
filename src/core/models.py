from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_path: str
    css_path: str
    title: str
    assignatura: str
    professor: str
    data: str
