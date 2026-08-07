from pathlib import Path

from src.core.models import ExportOptions
from src.infrastructure.config_repo import load_institut_config
from src.infrastructure.pandoc_converter import convert_markdown
from src.infrastructure.project_paths import from_project_root


def execute_export(options: ExportOptions) -> str:
    """Executa l'exportació d'un document Markdown a HTML/PDF.

    Args:
        options: Opcions d'exportació (ruta, títol, color, format, etc.).

    Returns:
        La ruta del fitxer generat.
    """
    config = load_institut_config()

    extension = "pdf" if options.format == "pdf" else "html"
    output_filename = f"{Path(options.md_path).stem}.{extension}"
    output_path = str(Path(options.output_dir) / output_filename)

    css_path = str(from_project_root("styles", config["css_name"]))
    template_path = str(from_project_root("templates", config["template_name"]))
    js_path = str(from_project_root("scripts", config["js_name"]))

    metadata = {
        **config,
        "title": options.title,
        "subtitol": options.subtitol,
        "data": options.data,
        "departament": options.departament,
        "primary_color": options.primary_color,
    }

    convert_markdown(
        md_path=options.md_path,
        output_path=output_path,
        css_path=css_path,
        template_path=template_path,
        js_path=js_path,
        highlight_style=config["highlight_style"],
        metadata=metadata,
    )
    return output_path

