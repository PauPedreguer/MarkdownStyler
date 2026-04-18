import subprocess
from typing import Dict, Any
from pathlib import Path

def convert_markdown(md_path: str, output_path: str, css_path: str, template_path: str, js_path: str, highlight_style: str, metadata: Dict[str, Any]):
    current_dir = Path(__file__).parent.parent.parent # Arrel del projecte
    
    # Afegir el JS a la metadata per a la plantilla
    if js_path:
        metadata["js"] = str(Path(js_path).absolute())

    cmd = [
        "pandoc",
        md_path,
        "-o", output_path,
        "-t", "html5",
        "--standalone",
        "--embed-resources",       # Incrusta imatges, CSS i JS en l'HTML final
        "--toc",
        "--toc-depth=3",
        "--mathml",                # Renderitza matemàtiques com a MathML natiu (funciona offline)
        f"--highlight-style={highlight_style}",
        f"--template={Path(template_path).absolute()}",
        f"--resource-path=.:{current_dir}:{current_dir}/templates:{current_dir}/scripts:{current_dir}/styles" 
    ]

    if css_path:
        abs_css = Path(css_path).absolute()
        cmd.append(f"--css={abs_css}")

    for key, value in metadata.items():
        if value:
            cmd.append(f"--metadata={key}:{value}")

    # Log de la comanda per a debug
    print(f"Executant Pandoc: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
