from src.core.models import ExportOptions
from src.infrastructure.config_repo import load_institut_config
from src.infrastructure.pandoc_converter import convert_markdown
from pathlib import Path


def execute_export(options: ExportOptions) -> str:
    config = load_institut_config()
    output_path = str(Path(options.output_dir) / f"{Path(options.md_path).stem}.html")
    css_path = str(Path("styles") / config["css_name"])
    template_path = str(Path("templates") / config["template_name"])
    js_path = str(Path("scripts") / config["js_name"])
    
    metadata = {
        **config,
        "title": options.title,
        "data": options.data,
        "primary_color": options.primary_color
    }
    
    convert_markdown(
        md_path=options.md_path,
        output_path=output_path,
        css_path=css_path,
        template_path=template_path,
        js_path=js_path,
        highlight_style=config["highlight_style"],
        metadata=metadata
    )
    return output_path
