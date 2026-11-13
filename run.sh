#!/bin/bash
# Llançador de Markdown Styler: executa sempre el codi d'este projecte,
# preferint l'intèrpret del .venv local.
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

exec "$PYTHON" main.py "$@"
