#!/bin/bash
# Genera un PDF a partir d'un Markdown: crea l'HTML amb Markdown Styler i
# l'imprimeix amb Chromium headless (portada, índex, capçaleres i número de
# pàgina, gràcies a les regles @page de styles/prova.css).
#
# Ús: ./pdf.sh fitxer.md [carpeta-destí]
set -u

if [ "$#" -lt 1 ]; then
    echo "Ús: ./pdf.sh fitxer.md [carpeta-destí]" >&2
    exit 2
fi

# Resol les rutes ABANS de canviar de directori, perquè les rutes relatives
# de l'usuari no es trenquen en saltar a l'arrel del projecte.
case "$1" in
    /*) MD="$1" ;;
    *)  MD="$PWD/$1" ;;
esac

if [ "$#" -ge 2 ]; then
    case "$2" in
        /*) OUT="$2" ;;
        *)  OUT="$PWD/$2" ;;
    esac
else
    OUT="${MD%/*}"
fi

# Situar-se a l'arrel del projecte sense dependre de l'ordre extern `dirname`.
case "$0" in
    */*) cd "${0%/*}" || exit 1 ;;
esac

if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    echo "Avís: no s'ha trobat .venv/bin/python; s'usa el python3 del sistema." >&2
    PYTHON="python3"
else
    echo "Error: no s'ha trobat cap intèrpret de Python." >&2
    echo "Crea l'entorn virtual amb:" >&2
    echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

exec "$PYTHON" main.py --pdf "$MD" --out "$OUT"
