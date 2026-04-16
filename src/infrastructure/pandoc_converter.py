import subprocess
from typing import Dict, Any

def convert_markdown(md_path: str, output_path: str, css_path: str, metadata: Dict[str, Any]):
    cmd = [
        "pandoc",
        md_path,
        "-o", output_path,
        "-t", "html5",
        "--standalone",            # HTML complet
        "--toc",                   # Taula de continguts
        "--toc-depth=3",
        "--highlight-style=zenburn",
        "--template=templates/base.html"
    ]

    if css_path:
        cmd.append(f"--css={css_path}")

    for key, value in metadata.items():
        if value:
            cmd.append(f"--metadata={key}:{value}")

    subprocess.run(cmd, check=True)
