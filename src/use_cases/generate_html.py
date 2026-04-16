from src.core.models import ExportOptions
from src.infrastructure.config_repo import load_institut_config
from src.infrastructure.pandoc_converter import convert_markdown

def execute_export(options: ExportOptions) -> None:
    config = load_institut_config()
    
    metadata = {
        **config,
        "title": options.title,
        "data": options.data
    }
    
    convert_markdown(
        md_path=options.md_path,
        output_path=options.output_path,
        css_path=options.css_path,
        metadata=metadata
    )
