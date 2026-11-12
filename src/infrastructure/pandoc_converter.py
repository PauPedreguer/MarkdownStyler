import re
import html as html_module
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from src.infrastructure.highlight_styles import ruta_estil_ressaltat
from src.infrastructure.project_paths import PROJECT_ROOT, from_project_root


class PandocError(RuntimeError):
    """Error en executar Pandoc.

    Conserva el missatge d'error (stderr) que ha emès Pandoc perquè la
    interfície el puga mostrar a l'usuari en lloc d'un error genèric.

    Attributes:
        stderr: Text complet de l'error emès per Pandoc (pot estar buit).
    """

    def __init__(self, message: str, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


def _text(value: Any) -> str:
    """Retorna el text d'un valor de subprocess de manera segura.

    Els tests substitueixen ``subprocess.run`` per un mock, de manera que
    ``stderr`` pot no ser una cadena. Aquest helper evita errors de tipus.

    Args:
        value: Valor a normalitzar (normalment ``CompletedProcess.stderr``).

    Returns:
        El text sense espais sobrants, o cadena buida si no és text.
    """
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return ""


# Metadades que la plantilla publica com a variables CSS (--doc-*) perquè les
# puguen usar les capçaleres i peus de pàgina (@page) en imprimir.
_CSS_METADATA_KEYS = ("institut_nom", "departament", "assignatura", "curs", "data")


def _css_escape(value: Any) -> str:
    """Escapa un text per a poder-lo posar dins d'una cadena CSS ("...").

    Pandoc escapa l'HTML però no el CSS, i la plantilla publica algunes
    metadades dins d'un bloc ``<style>`` (``--doc-*``). Una cometa doble o una
    barra invertida en un títol trencaria el CSS.

    Args:
        value: Valor de la metadada (es converteix a text).

    Returns:
        El text amb barres invertides, cometes i salts de línia escapats.
    """
    if value is None:
        return ""
    text = str(value)
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r\n", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


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
    path = Path(html_path)
    # Guard defensiu: si pandoc no ha generat el fitxer (error silenciós,
    # execució simulada als tests, etc.) no hi ha res a postprocessar.
    if not path.is_file():
        return

    content = path.read_text(encoding="utf-8")

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
    # Optimització: com que el contingut del div mermaid ja no conté etiquetes
    # HTML (s'han eliminat a la passada anterior), podem usar [^<]* en lloc de
    # .*? amb re.DOTALL, que era molt més lent en fitxers grans.
    new_content = re.sub(
        r'<div class="sourceCode"[^>]*>\s*(<div class="mermaid">[^<]*</div>)\s*</div>',
        r'\1',
        new_content,
    )

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")






def convert_markdown(
    md_path: str,
    output_path: str,
    css_path: str,
    template_path: str,
    js_path: str,
    highlight_style: str,
    metadata: Dict[str, Any],
) -> None:
    """Converteix un fitxer Markdown a HTML mitjançant Pandoc.

    L'aplicació només genera HTML: el PDF s'obté imprimint el document des del
    navegador (botó 🖨️ del propi document o l'script ``pdf.sh``).

    Args:
        md_path: Ruta del fitxer Markdown d'entrada.
        output_path: Ruta del fitxer HTML de sortida.
        css_path: Ruta relativa del full d'estil CSS.
        template_path: Ruta relativa de la plantilla HTML.
        js_path: Ruta relativa de l'script JS.
        highlight_style: Estil de ressaltat de codi de Pandoc (nom d'un tema
            incorporat o ruta d'un fitxer ``.theme`` del projecte).
        metadata: Diccionari de metadades per a la plantilla.
    """
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
        f"--highlight-style={ruta_estil_ressaltat(highlight_style)}",
        f"--template={from_project_root(template_path).resolve()}",
        f"--resource-path=.:{PROJECT_ROOT}:{from_project_root('templates')}:{from_project_root('scripts')}:{from_project_root('styles')}",
        "--katex",
    ]

    # Combinar el CSS base (compartit) amb el CSS específic de l'estil triat en
    # un sol fitxer temporal. Passar dos --css a pandoc amb --embed-resources
    # pot fallar, així que concatenem els fitxers en un únic CSS. L'estil
    # específic es carrega DESPRÉS del base, de manera que pot sobreescriure
    # els seus valors.
    css_files = []
    base_css = from_project_root("styles", "base.css")
    if base_css.exists():
        css_files.append(base_css.resolve())
    if css_path:
        abs_css = from_project_root(css_path).resolve()
        css_files.append(abs_css)

    temp_css = None
    if css_files:
        # Concatenar tots els fitxers CSS en un de temporal
        temp_css = tempfile.NamedTemporaryFile(
            mode="w", suffix=".css", delete=False, encoding="utf-8"
        )
        for f in css_files:
            with open(f, "r", encoding="utf-8") as fh:
                temp_css.write(fh.read())
                temp_css.write("\n")
        temp_css.close()
        cmd.append(f"--css={temp_css.name}")

    # Metadades escapades per al CSS de la plantilla (--doc-*). Es fa una
    # còpia per clau perquè els valors originals han de quedar intactes per a
    # l'HTML (títols, noms, etc.).
    for key in _CSS_METADATA_KEYS:
        metadata[f"{key}_css"] = _css_escape(metadata.get(key, ""))

    for key, value in metadata.items():
        if value:
            cmd.append(f"--metadata={key}:{value}")

    # Log de la comanda per a debug
    print(f"Executant Pandoc: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        stderr = _text(exc.stderr)
        detall = f"\n{stderr}" if stderr else ""
        raise PandocError(
            f"Pandoc ha fallat amb el codi {exc.returncode}.{detall}", stderr
        ) from exc
    finally:
        # Netejar el fitxer CSS temporal
        if temp_css is not None and os.path.exists(temp_css.name):
            os.remove(temp_css.name)

    # Pandoc pot emetre avisos (per exemple, de WeasyPrint) tot i acabar bé:
    # mostrar-los evita que l'usuari els perda.
    avisos = _text(getattr(result, "stderr", None))
    if avisos:
        print(f"Pandoc avisa: {avisos}")


    # Postprocessar els blocs mermaid. Es fa DESPRÉS de pandoc per evitar que
    # els caràcters especials del diagrama siguin escapats.
    _postprocess_mermaid(output_path)



