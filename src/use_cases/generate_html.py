from pathlib import Path

from src.core.identitats import identitat_efectiva
from src.core.models import ExportOptions
from src.infrastructure.config_repo import load_institut_config
from src.infrastructure.pandoc_converter import convert_markdown
from src.infrastructure.project_paths import from_project_root

# Claus de la configuració que són només per a l'aplicació: si s'envien a pandoc
# acaben a la línia d'ordres com un text amb claudàtors i cometes (les
# plantilles no en poden traure res de bo).
METADADES_INTERNES = frozenset({"identitats"})


def execute_export(options: ExportOptions) -> str:
    """Executa l'exportació d'un document Markdown a HTML.

    L'aplicació només genera HTML; el PDF s'obté imprimint el document des del
    navegador (botó 🖨️ del propi document o l'script ``pdf.sh``), que aplica
    les regles ``@page`` del full d'estil.

    Args:
        options: Opcions d'exportació (ruta, títol, color, etc.).

    Returns:
        La ruta del fitxer HTML generat.
    """
    config = load_institut_config()

    output_path = str(Path(options.output_dir) / f"{Path(options.md_path).stem}.html")

    css_path = str(from_project_root("styles", config["css_name"]))
    template_path = str(from_project_root("templates", config["template_name"]))
    js_path = str(from_project_root("scripts", config["js_name"]))

    # El color triat a la finestra pot no portar curs ni assignatura: en eixe
    # cas manen els del document per defecte (la primera identitat).
    identitat = identitat_efectiva(config["identitats"], options.primary_color)

    metadata = {
        **{
            clau: valor
            for clau, valor in config.items()
            if clau not in METADADES_INTERNES
        },
        "title": options.title,
        "subtitol": options.subtitol,
        "data": options.curs_academic,
        # Si l'opció no porta departament, es respecta el de la configuració
        # de l'institut (abans es trepitjava amb un valor fix "Informàtica").
        "departament": options.departament or config.get("departament", ""),
        # El curs i l'assignatura venen del color d'identitat triat a la
        # finestra; si el color no en porta, manen els de la primera identitat
        # de la configuració (el document per defecte).
        "curs": options.curs or identitat["curs"],
        "assignatura": options.assignatura or identitat["assignatura"],
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

