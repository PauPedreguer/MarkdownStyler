from core.converter import convert_markdown

def process(md_path: str, css_path: str, output_path: str, metadata: dict):
    convert_markdown(md_path, output_path, css_path, metadata)