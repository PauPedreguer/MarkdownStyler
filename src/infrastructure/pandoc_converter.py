import subprocess
from typing import Dict, Any
from pathlib import Path
from src.infrastructure.project_paths import PROJECT_ROOT, from_project_root


def convert_markdown(
    md_path: str,
    output_path: str,
    css_path: str,
    template_path: str,
    js_path: str,
    highlight_style: str,
    metadata: Dict[str, Any],
) -> None:
    """Converteix un fitxer Markdown a HTML/PDF mitjançant Pandoc.

    Args:
        md_path: Ruta del fitxer Markdown d'entrada.
        output_path: Ruta del fitxer de sortida (.html o .pdf).
        css_path: Ruta relativa del full d'estil CSS.
        template_path: Ruta relativa de la plantilla HTML.
        js_path: Ruta relativa de l'script JS.
        highlight_style: Estil de ressaltat de codi de Pandoc.
        metadata: Diccionari de metadades per a la plantilla.
    """
    # Determinar si és exportació a PDF
    is_pdf = output_path.lower().endswith(".pdf")
    if is_pdf:
        metadata["pdf_export"] = True
        # Usar el CSS especialitzat per a PDF si està disponible
        pdf_css = from_project_root("styles", "pdf.css")
        if pdf_css.exists():
            css_path = "styles/pdf.css"

    # Afegir el JS a la metadata per a la plantilla
    if js_path:
        metadata["js"] = str(from_project_root(js_path).resolve())

    cmd = [
        "pandoc",
        md_path,
        "-o", output_path,
        "-t", "html5",
        "--standalone",
        "--embed-resources",
        "--toc",
        "--toc-depth=3",
        f"--highlight-style={highlight_style}",
        f"--template={from_project_root(template_path).resolve()}",
        f"--resource-path=.:{PROJECT_ROOT}:{from_project_root('templates')}:{from_project_root('scripts')}:{from_project_root('styles')}",
    ]

    if is_pdf:
        cmd.append("--pdf-engine=weasyprint")
        cmd.append("--pdf-engine-opt=--presentational-hints")
        cmd.append("--webtex")
    else:
        cmd.append("--katex")

    if css_path:
        abs_css = from_project_root(css_path).resolve()
        cmd.append(f"--css={abs_css}")

    for key, value in metadata.items():
        if value:
            cmd.append(f"--metadata={key}:{value}")

    # Log de la comanda per a debug
    print(f"Executant Pandoc: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

