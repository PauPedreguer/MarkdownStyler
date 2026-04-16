from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_path: str
    css_path: str
    title: str
    data: str
