import subprocess
from pathlib import Path

def convert_markdown(md_path: str, output_path: str, css_path: str, metadata: dict):
    cmd = [
        "pandoc",
        md_path,
        "-o", output_path,
        "-t", "html5",
        "--standalone",            # HTML complet
        "--toc",                   # Taula de continguts
        "--toc-depth=3",
        "--highlight-style=zenburn",
        f"--template=templates/base.html"
    ]

    # Afegir CSS
    if css_path:
        cmd.append(f"--css={css_path}")

    # Afegir metadata
    for key, value in metadata.items():
        cmd.append(f"--metadata={key}:{value}")

    subprocess.run(cmd, check=True)