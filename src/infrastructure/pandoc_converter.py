import re
import html as html_module
import subprocess
from typing import Dict, Any
from src.infrastructure.project_paths import PROJECT_ROOT, from_project_root



def _postprocess_mermaid(html_path: str) -> None:
    """Converteix els blocs de codi mermaid de l'HTML generat en <div class="mermaid">.

    Pandoc tracta els diagrames mermaid com a blocs de codi normals, generant
    una estructura com:
        <div class="sourceCode"><pre class="sourceCode mermaid"><code>...</code></pre></div>

    Aquest postprocessat (fet DESPRÉS de pandoc) els transforma en contenidors
    que mermaid.js pot renderitzar al navegador. Fer-ho després de pandoc evita
    que els caràcters especials del diagrama (com -->, &, etc.) siguin escapats.

    Args:
        html_path: Ruta del fitxer HTML generat per pandoc.
    """
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Patró robust per trobar blocs de codi mermaid generats per pandoc.
    # Pandoc pot generar estructures lleugerament diferents, per això busquem
    # qualsevol <pre> amb classe que contingui "mermaid" seguit d'un <code>.
    # Exemple típic:
    #   <div class="sourceCode" id="cbN"><pre class="sourceCode mermaid"><code class="sourceCode mermaid">...</code></pre></div>
    pattern = re.compile(
        r'<pre[^>]*class="[^"]*\bmermaid\b[^"]*"[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>',
        re.DOTALL,
    )

    def replace(match):
        diagram = match.group(1)
        # Desescapar les entitats HTML que pandoc hagi pogut generar
        diagram = html_module.unescape(diagram)

        # Eliminar els enllaços de numeració de línies que pandoc afegeix
        diagram = re.sub(r'<a[^>]*>.*?</a>', '', diagram)
        # Eliminar les etiquetes span (obertura i tancament) però CONSERVAR el text
        diagram = re.sub(r'</?span[^>]*>', '', diagram)
        # Eliminar qualsevol altra etiqueta residual
        diagram = re.sub(r'<[^>]+>', '', diagram)
        return '<div class="mermaid">\n' + diagram.strip() + '\n</div>'

    new_content = pattern.sub(replace, content)

    # Netejar els <div class="sourceCode"> buits que hagin quedat al voltant
    # del div mermaid (pandoc els genera com a contenidor del bloc de codi).
    new_content = re.sub(
        r'<div class="sourceCode"[^>]*>\s*(<div class="mermaid">.*?</div>)\s*</div>',
        r'\1',
        new_content,
        flags=re.DOTALL,
    )

    if new_content != content:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_content)




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

    # Postprocessar els blocs mermaid (només per a HTML, no per a PDF).
    # Es fa DESPRÉS de pandoc per evitar que els caràcters especials del
    # diagrama siguin escapats.
    if not is_pdf:
        _postprocess_mermaid(output_path)



