# -*- mode: python ; coding: utf-8 -*-
"""Especificació de PyInstaller per a Markdown Styler.

Construeix l'aplicació en mode *onedir* (una carpeta amb l'executable i tots
els recursos), que és el que fan servir els paquets .deb/.rpm, l'AppImage i
l'instal·lador de Windows: arranca més de pressa que *onefile* i les
biblioteques de Qt queden com a fitxers separats, tal com demana la LGPL.

Normalment no es crida a mà: ho fa ``build.sh``, que abans prepara un arbre de
codi net a ``packaging/build/arrel`` i passa la ruta per ``MS_ARREL``.

    MS_ARREL=$PWD/packaging/build/arrel pyinstaller packaging/markdown-styler.spec
"""

import os
from pathlib import Path

# Arrel del codi que s'empaqueta: la que passa build.sh o, si no, l'arrel del
# projecte (el directori pare d'este fitxer).
ARREL = (
    Path(os.environ["MS_ARREL"]).resolve()
    if os.environ.get("MS_ARREL")
    else Path(SPECPATH).resolve().parent
)

# Recursos que viatgen amb l'aplicació (es busquen amb RESOURCE_ROOT).
# S'afigen carpeta a carpeta, i no el projecte sencer, perquè no s'hi coli res
# que no toca (configuració real, .git, .venv, exemples…).
CARPETES_RECURSOS = ("styles", "templates", "scripts", "themes", "assets")

# La configuració hi va com a exemple: la de l'usuari es crea al seu directori
# de dades la primera vegada que arranca l'aplicació.
FITXERS_RECURSOS = (
    ("config/institut.exemple.json", "config"),
    ("LICENSE", "."),
    ("THIRD-PARTY.md", "."),
    ("README.md", "."),
)

datas = []
for carpeta in CARPETES_RECURSOS:
    origen = ARREL / carpeta
    if origen.is_dir():
        datas.append((str(origen), carpeta))

for fitxer, desti in FITXERS_RECURSOS:
    origen = ARREL / fitxer
    if origen.is_file():
        datas.append((str(origen), desti))

# Pandoc empaquetat (el baixa build.sh a packaging/build/bin). Si no hi és, la
# instància empaquetada fa servir el pandoc del PATH.
PANDOC = ARREL / "bin" / ("pandoc.exe" if os.name == "nt" else "pandoc")
if PANDOC.is_file():
    datas.append((str(PANDOC), "bin"))

# Icona de l'executable de Windows.
ICONA = Path(os.environ.get("MS_ICONA") or (Path(SPECPATH) / "build" / "icona.ico"))

a = Analysis(
    [str(ARREL / "main.py")],
    pathex=[str(ARREL)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Tkinter no s'usa enlloc i arrossega mitja biblioteca estàndard.
    excludes=["tkinter", "unittest", "pydoc_data"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="markdown-styler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ICONA) if ICONA.is_file() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="markdown-styler",
)
