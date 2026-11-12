"""Punt d'entrada de Markdown Styler.

Per defecte obri la interfície gràfica. Amb ``--pdf`` converteix un Markdown en
PDF sense obrir cap finestra: genera l'HTML amb l'aplicació i l'imprimeix amb
Chromium headless (és el que fa servir ``pdf.sh``).

Els imports de PyQt6 es fan dins de ``_obri_interficie()`` perquè el mode PDF
funcione en entorns sense entorn gràfic.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from src.core.curs import calcular_curs_academic
from src.infrastructure.project_paths import from_project_root

# Navegadors basats en Chromium que saben imprimir a PDF des de la línia d'ordres.
NAVEGADORS = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "chrome",
    "brave-browser",
    "microsoft-edge",
)


def aplica_tema(app_qt) -> None:
    """Aplica a l'aplicació l'estil Fusion i el full QSS de la interfície.

    L'ordre importa: ``setStyle()`` reconstrueix el motor d'estil i descarta
    part dels retocs que ha aplicat el ``setStyleSheet()``, de manera que
    primer s'ha de fixar l'estil (Fusion, consistent a totes les plataformes)
    i després carregar el QSS. El QSS es llig sempre en UTF-8 perquè no depén
    del locale del sistema (amb un locale no UTF-8 fallaria o es veuria mal).

    Args:
        app_qt: Instància de ``QApplication``.
    """
    app_qt.setStyle("Fusion")

    style_path = from_project_root("src", "ui", "style.qss")
    if style_path.exists():
        app_qt.setStyleSheet(style_path.read_text(encoding="utf-8"))


def navegador_chromium():
    """Retorna la ruta del primer navegador Chromium disponible al PATH.

    Returns:
        La ruta de l'executable, o ``None`` si no n'hi ha cap instal·lat.
    """
    for nom in NAVEGADORS:
        ruta = shutil.which(nom)
        if ruta:
            return ruta
    return None


def genera_pdf(md_path, output_dir=".", title="", curs_academic=""):
    """Genera l'HTML amb l'aplicació i el converteix a PDF amb Chromium.

    La maquetació del PDF (portada, índex, capçaleres i número de pàgina) la
    fan les regles ``@page`` de ``styles/prova.css``.

    Args:
        md_path: Fitxer Markdown d'origen.
        output_dir: Carpeta on deixar l'HTML i el PDF.
        title: Títol del document (per defecte, el nom del fitxer).
        curs_academic: Curs acadèmic (per defecte, el calculat).

    Returns:
        La ruta (``Path``) del PDF generat.

    Raises:
        RuntimeError: Si no hi ha cap navegador Chromium instal·lat.
        FileNotFoundError: Si el fitxer Markdown no existeix.
        PandocError: Si Pandoc falla en generar l'HTML.
    """
    from src.core.models import ExportOptions
    from src.use_cases.generate_html import execute_export

    navegador = navegador_chromium()
    if navegador is None:
        raise RuntimeError(
            "No s'ha trobat cap navegador Chromium al PATH (chromium, "
            "chromium-browser o google-chrome). Cal per a generar el PDF."
        )

    md = Path(md_path).expanduser()
    if not md.is_file():
        raise FileNotFoundError(f"No s'ha trobat el fitxer: {md}")
    md = md.resolve()

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = Path(
        execute_export(
            ExportOptions(
                md_path=str(md),
                output_dir=str(out_dir),
                title=title or md.stem,
                curs_academic=curs_academic or calcular_curs_academic(),
            )
        )
    )

    pdf_path = html_path.with_suffix(".pdf")
    # --virtual-time-budget dóna temps al JS (mermaid, clonat del sumari) a
    # acabar abans d'imprimir; --no-pdf-header-footer lleva la capçalera que
    # afig el navegador, perquè les capçaleres útils les posa @page.
    subprocess.run(
        [
            navegador,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=15000",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return pdf_path


def _obri_interficie() -> int:
    """Obri la finestra de l'aplicació.

    Returns:
        El codi d'eixida de Qt.
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication

    from src.ui.app import App

    # Suport per a pantalles d'alta resolució (Retina/4K)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app_qt = QApplication(sys.argv)
    aplica_tema(app_qt)

    window = App()
    window.show()
    return app_qt.exec()


def main(argv=None) -> int:
    """Punt d'entrada: interfície gràfica o conversió a PDF (``--pdf``).

    Args:
        argv: Arguments de línia d'ordres (per defecte, ``sys.argv``).

    Returns:
        El codi d'eixida del procés.
    """
    parser = argparse.ArgumentParser(
        prog="markdown-styler",
        description="Genera documents amb estil a partir de Markdown.",
    )
    parser.add_argument("markdown", nargs="?", help="fitxer .md (només amb --pdf)")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="genera el PDF sense obrir la interfície gràfica",
    )
    parser.add_argument(
        "--out",
        default=".",
        help="carpeta de destí (per defecte, la carpeta actual)",
    )
    parser.add_argument("--title", default="", help="títol del document")
    parser.add_argument(
        "--curs",
        dest="curs_academic",
        default="",
        help="curs acadèmic, p. ex. 26-27 (per defecte, el calculat)",
    )
    args = parser.parse_args(argv)

    if not args.pdf:
        return _obri_interficie()

    if not args.markdown:
        parser.error("--pdf necessita el fitxer Markdown d'entrada")

    try:
        pdf = genera_pdf(
            args.markdown,
            output_dir=args.out,
            title=args.title,
            curs_academic=args.curs_academic,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        missatge = "Error en imprimir el PDF amb el navegador."
        detall = (exc.stderr or "").strip()
        if detall:
            missatge += f"\n{detall}"
        print(missatge, file=sys.stderr)
        return 1

    print(pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
    

    