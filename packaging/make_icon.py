#!/usr/bin/env python3
"""Genera les icones PNG (i el .ico de Windows) a partir de l'SVG.

L'icona mestra és ``assets/markdown-styler.svg``. Este script la rasteritza
amb el mateix Qt que fa servir l'aplicació, de manera que no cal cap eina
externa (Inkscape, ImageMagick…) ni cap dependència nova.

    python3 packaging/make_icon.py --out packaging/build/icones

Deixa els PNG a ``<out>/<mida>x<mida>.png`` i, amb ``--ico``, un
``icona.ico`` amb totes les mides (format ICO amb PNG a dins, que és el que
entén Windows Vista i posteriors).
"""
import argparse
import os
import struct
import sys
from pathlib import Path

# Sense pantalla: la rasterització no en necessita cap.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QRectF, Qt  # noqa: E402
from PyQt6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PyQt6.QtSvg import QSvgRenderer  # noqa: E402

MATRIU = Path(__file__).resolve().parent.parent
SVG_DEFECTE = MATRIU / "assets" / "markdown-styler.svg"

MIDES = (16, 24, 32, 48, 64, 128, 256, 512)


def _imatge(renderer: QSvgRenderer, costat: int) -> QImage:
    """Rasteritza l'SVG a una imatge quadrada amb fons transparent."""
    imatge = QImage(costat, costat, QImage.Format.Format_ARGB32)
    imatge.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(imatge)
    pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
    pintor.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(pintor, QRectF(0, 0, costat, costat))
    pintor.end()
    return imatge


def desa_png(renderer: QSvgRenderer, costat: int, desti: Path) -> None:
    """Desa una imatge PNG de ``costat`` x ``costat`` píxels."""
    if not _imatge(renderer, costat).save(str(desti), "PNG"):
        raise SystemExit(f"No s'ha pogut escriure {desti}")


def desa_ico(pngs: list, desti: Path) -> None:
    """Escriu un .ico amb els PNG indicats.

    Args:
        pngs: Llista de tuples ``(costat, dades_png)``.
        desti: Fitxer .ico de sortida.
    """
    capcalera = struct.pack("<HHH", 0, 1, len(pngs))
    desplacament = 6 + 16 * len(pngs)
    entrades = b""
    dades = b""
    for costat, contingut in pngs:
        # Al format ICO, 256 es guarda com a 0.
        mida = 0 if costat >= 256 else costat
        entrades += struct.pack(
            "<BBBBHHII", mida, mida, 0, 0, 1, 32, len(contingut), desplacament
        )
        desplacament += len(contingut)
        dades += contingut
    desti.write_bytes(capcalera + entrades + dades)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Genera les icones de l'aplicació.")
    parser.add_argument("--svg", default=str(SVG_DEFECTE), help="SVG d'origen")
    parser.add_argument("--out", required=True, help="carpeta de destí dels PNG")
    parser.add_argument(
        "--ico", action="store_true", help="genera també un icona.ico (Windows)"
    )
    args = parser.parse_args(argv)

    svg = Path(args.svg)
    if not svg.is_file():
        parser.error(f"no s'ha trobat l'SVG: {svg}")

    sortida = Path(args.out)
    sortida.mkdir(parents=True, exist_ok=True)

    app = QGuiApplication(sys.argv[:1])
    renderer = QSvgRenderer(str(svg))
    if not renderer.isValid():
        raise SystemExit(f"L'SVG no és vàlid: {svg}")

    mides_ico = []
    for costat in MIDES:
        desti = sortida / f"{costat}x{costat}.png"
        desa_png(renderer, costat, desti)
        print(f"  {desti}")
        if args.ico:
            temporal = sortida / f".{costat}.png"
            desa_png(renderer, costat, temporal)
            mides_ico.append((costat, temporal.read_bytes()))
            temporal.unlink()

    if args.ico:
        desti = sortida / "icona.ico"
        desa_ico(mides_ico, desti)
        print(f"  {desti}")

    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
