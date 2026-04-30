import subprocess
from typing import Dict, Any
from pathlib import Path
from src.infrastructure.project_paths import PROJECT_ROOT

def convert_markdown(md_path: str, output_path: str, css_path: str, template_path: str, js_path: str, highlight_style: str, metadata: Dict[str, Any]):
    # Arrel del projecte per a convertir rutes relatives a absolutes
    current_dir = PROJECT_ROOT

    # Determinar si és exportació a PDF
    is_pdf = output_path.lower().endswith(".pdf")
    if is_pdf:
        metadata["pdf_export"] = True
        # Use specialized PDF CSS if available
        pdf_css = current_dir / "styles" / "pdf.css"
        if pdf_css.exists():
            css_path = "styles/pdf.css"

    # Afegir el JS a la metadata per a la plantilla
    if js_path:
        metadata["js"] = str((current_dir / js_path).resolve())

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
        f"--template={(current_dir / template_path).resolve()}",
        f"--resource-path=.:{current_dir}:{current_dir}/templates:{current_dir}/scripts:{current_dir}/styles"
    ]

    if is_pdf:
        cmd.append("--pdf-engine=weasyprint")
        cmd.append("--pdf-engine-opt=--presentational-hints")
        cmd.append("--webtex")
    else:
        cmd.append("--katex")

    if css_path:
        abs_css = (current_dir / css_path).resolve()
        cmd.append(f"--css={abs_css}")

    for key, value in metadata.items():
        if value:
            cmd.append(f"--metadata={key}:{value}")

    # Log de la comanda per a debug
    print(f"Executant Pandoc: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
