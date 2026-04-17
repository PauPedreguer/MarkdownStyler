from dataclasses import dataclass

@dataclass
class ExportOptions:
    md_path: str
    output_path: str
    css_path: str
    template_path: str
    js_path: str
    title: str
    data: str
    primary_color: str = "#1d4ed8"
