#!/usr/bin/env bash
# Construeix els paquets de Markdown Styler.
#
#   ./build.sh deb        # .deb (Debian, Ubuntu, Mint)
#   ./build.sh rpm        # .rpm (Fedora, openSUSE)
#   ./build.sh appimage   # AppImage (qualsevol Linux, sense instal·lar)
#   ./build.sh all        # els tres anteriors
#   ./build.sh dir        # només el bundle de PyInstaller (per a proves)
#   ./build.sh icones     # regenera les icones a packaging/build/icones
#   ./build.sh escriptori # icona al menú per a l'usuari actual (--codi,
#                         # --appimage, --escriptori, --elimina)
#   ./build.sh clean      # esborra packaging/build i packaging/dist
#
# Requisits: Python 3.10+ amb pip i connexió a Internet (per a PyInstaller,
# PyQt6 i Pandoc). A Linux, a més: dpkg-deb per al .deb i rpmbuild per al
# .rpm; l'AppImage el baixa tot sol.
#
# Variables d'entorn:
#   PYTHON           intèrpret per a l'entorn d'empaquetat (per defecte python3)
#   PANDOC_VERSIO    versió de Pandoc a empaquetar (per defecte 3.14)
#   PANDOC_SHA256    sha256 esperat del tarball de Pandoc (opcional)
#   SENSE_PANDOC=1   no empaqueta Pandoc (fa servir el del PATH)
#   SENSE_XARXA=1    no baixa res: usa el que ja hi ha a la memòria cau
set -euo pipefail

ARREL_PROJECTE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$ARREL_PROJECTE"

VERSIO=$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' src/version.py)
: "${VERSIO:?no es pot llegir la versio de src/version.py}"
PANDOC_VERSIO=${PANDOC_VERSIO:-3.14}
PYTHON=${PYTHON:-python3}

BUILD="$ARREL_PROJECTE/packaging/build"
DIST="$BUILD/dist"
WORK="$BUILD/pyinstaller"
MEMORIA="$BUILD/cache"
ARBRE="$BUILD/arrel"
ICONES="$BUILD/icones"
SAIDA="$ARREL_PROJECTE/packaging/dist"
VENV="$BUILD/venv"


# Directori dels executables de l'entorn virtual (bin/ a Linux, Scripts/ al Windows).
bin_venv() {
    if [ -d "$VENV/Scripts" ]; then
        printf '%s\n' "$VENV/Scripts"
    else
        printf '%s\n' "$VENV/bin"
    fi
}

info() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
avis() { printf '\033[1;33mAvís:\033[0m %s\n' "$*" >&2; }
mor() { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

comprova_eina() {
    command -v "$1" >/dev/null 2>&1 || mor "cal l'eina «$1» per a este objectiu"
}

prepara_venv() {
    VENV_BIN=$(bin_venv)
    if [ ! -x "$VENV/bin/python" ] && [ ! -x "$VENV/Scripts/python.exe" ]; then
        info "Cree entorn d'empaquetat a packaging/build/venv"
        "$PYTHON" -m venv "$VENV"
        VENV_BIN=$(bin_venv)
        "$VENV_BIN/python" -m pip install --quiet --upgrade pip
        "$VENV_BIN/python" -m pip install --quiet \
            "PyInstaller>=6.16" "PyQt6>=6.6.0"
    fi
}

# --------------------------------------------------------------- pandoc ----
baixa_pandoc() {
    if [ "${SENSE_PANDOC:-0}" = "1" ]; then
        avis "SENSE_PANDOC=1: no s'empaqueta Pandoc (caldrà al PATH)."
        return
    fi

    case "$(uname -s)" in
        Linux)
            paquet="pandoc-${PANDOC_VERSIO}-linux-amd64.tar.gz"
            nom="pandoc"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            paquet="pandoc-${PANDOC_VERSIO}-windows-x86_64.zip"
            nom="pandoc.exe"
            ;;
        *)
            mor "no sé com baixar Pandoc per a $(uname -s)"
            ;;
    esac

    desti="$ARBRE/bin"
    mkdir -p "$desti" "$MEMORIA"

    if [ -f "$desti/$nom" ]; then
        return
    fi

    if [ ! -f "$MEMORIA/$paquet" ]; then
        if [ "${SENSE_XARXA:-0}" = "1" ]; then
            mor "SENSE_XARXA=1 i no hi ha $paquet a la memòria cau"
        fi
        info "Baixe Pandoc $PANDOC_VERSIO ($paquet)"
        url="https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSIO}/${paquet}"
        curl -fL --retry 3 -o "$MEMORIA/$paquet" "$url" \
            || mor "no s'ha pogut baixar $url"
    fi

    if [ -n "${PANDOC_SHA256:-}" ]; then
        printf '%s  %s\n' "$PANDOC_SHA256" "$MEMORIA/$paquet" | sha256sum -c - >/dev/null \
            || mor "el sha256 de Pandoc no coincidix"
    fi

    case "$paquet" in
        *.tar.gz)
            tar -xzf "$MEMORIA/$paquet" -C "$MEMORIA"
            cp "$MEMORIA/pandoc-${PANDOC_VERSIO}/bin/pandoc" "$desti/pandoc"
            ;;
        *.zip)
            "$PYTHON" -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
                "$MEMORIA/$paquet" "$MEMORIA"
            cp "$MEMORIA/pandoc-${PANDOC_VERSIO}/pandoc.exe" "$desti/pandoc.exe"
            ;;
    esac
    chmod +x "$desti/$nom" 2>/dev/null || true
    info "Pandoc empaquetat a bin/$nom"
}

# --------------------------------------------------------------- arbre -----
prepara_arbre() {
    info "Prepare un arbre de codi net a packaging/build/arrel"
    rm -rf "$ARBRE"
    mkdir -p "$ARBRE"

    # Es copia només el que s'empaqueta: fora .git, .venv, tests, exemples i,
    # sobretot, les dades personals (config/institut.json i el logo del centre).
    tar -C "$ARREL_PROJECTE" \
        --exclude='./.git' \
        --exclude='./.github' \
        --exclude='./.venv' \
        --exclude='./.pytest_cache' \
        --exclude='./packaging' \
        --exclude='./tests' \
        --exclude='./examples' \
        --exclude='./build' \
        --exclude='./dist' \
        --exclude='./config/institut.json' \
        --exclude='./assets/logoIESPereMariaOrtsiBosch.png' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -cf - . | tar -C "$ARBRE" -xf -

    if [ -f "$ARBRE/config/institut.json" ]; then
        mor "l'arbre encara conté la configuració real del centre"
    fi

    baixa_pandoc
}

# --------------------------------------------------------------- icones ----
genera_icones() {
    info "Genera les icones a packaging/build/icones"
    VENV_BIN=$(bin_venv)
    "$VENV_BIN/python" packaging/make_icon.py --out "$ICONES" --ico
}

# --------------------------------------------------------------- bundle ----
construeix_bundle() {
    prepara_venv
    prepara_arbre
    genera_icones

    info "Executa PyInstaller"
    rm -rf "$DIST/markdown-styler"
    MS_ARREL="$ARBRE" MS_ICONA="$ICONES/icona.ico" \
        "$VENV_BIN/pyinstaller" \
        --noconfirm --clean \
        --distpath "$DIST" \
        --workpath "$WORK" \
        packaging/markdown-styler.spec >"$BUILD/pyinstaller.log" 2>&1 \
        || { tail -40 "$BUILD/pyinstaller.log"; mor "PyInstaller ha fallat (log a packaging/build/pyinstaller.log)"; }

    # A Windows l'executable porta .exe.
    EXECUTABLE="$DIST/markdown-styler/markdown-styler"
    if [ -f "$EXECUTABLE.exe" ]; then
        EXECUTABLE="$EXECUTABLE.exe"
    fi
    [ -f "$EXECUTABLE" ] || mor "no s'ha generat l'executable"
    "$EXECUTABLE" --version \
        || mor "l'executable generat no arranca"
}

# --------------------------------------------------------------- comú ------
# Copia el bundle, l'entrada d'escriptori, les metadades i les icones a un
# directori amb l'esquema FHS (/usr/...), que és el que comparteixen el .deb,
# el .rpm i l'AppImage.
omple_fhs() {
    local desti="$1"
    mkdir -p "$desti/usr/lib" "$desti/usr/bin" \
             "$desti/usr/share/applications" "$desti/usr/share/metainfo"

    cp -a "$DIST/markdown-styler" "$desti/usr/lib/markdown-styler"
    ln -sf ../lib/markdown-styler/markdown-styler "$desti/usr/bin/markdown-styler"
    install -m644 packaging/markdown-styler.desktop \
        "$desti/usr/share/applications/markdown-styler.desktop"
    install -m644 packaging/com.github.PauPedreguer.MarkdownStyler.appdata.xml \
        "$desti/usr/share/metainfo/com.github.PauPedreguer.MarkdownStyler.appdata.xml"

    local mida
    for mida in 16 24 32 48 64 128 256 512; do
        install -Dm644 "$ICONES/${mida}x${mida}.png" \
            "$desti/usr/share/icons/hicolor/${mida}x${mida}/apps/markdown-styler.png"
    done
}

# --------------------------------------------------------------- .deb ------
paquet_deb() {
    comprova_eina dpkg-deb
    [ -d "$DIST/markdown-styler" ] || construeix_bundle

    local arq paquet mida
    case "$(uname -m)" in
        x86_64) arq="amd64" ;;
        aarch64) arq="arm64" ;;
        *) mor "arquitectura no suportada: $(uname -m)" ;;
    esac

    paquet="$BUILD/deb"
    info "Munte el paquet .deb ($arq)"
    rm -rf "$paquet"
    omple_fhs "$paquet"

    mida=$(du -sk "$paquet" | cut -f1)
    mkdir -p "$paquet/DEBIAN"
    sed -e "s/@VERSIO@/$VERSIO/" \
        -e "s/@ARQUITECTURA@/$arq/" \
        -e "s/@MIDA_INSTALADA@/$mida/" \
        packaging/deb/control.in >"$paquet/DEBIAN/control"
    install -m755 packaging/deb/postinst "$paquet/DEBIAN/postinst"
    install -m755 packaging/deb/postrm "$paquet/DEBIAN/postrm"

    # Debian policy: cada paquet ha de dur el copyright i el text de la
    # llicència a /usr/share/doc/<paquet>/.
    install -Dm644 packaging/deb/copyright \
        "$paquet/usr/share/doc/markdown-styler/copyright"
    install -m644 THIRD-PARTY.md "$paquet/usr/share/doc/markdown-styler/"

    mkdir -p "$SAIDA"
    dpkg-deb --root-owner-group -Zxz --build "$paquet" \
        "$SAIDA/markdown-styler_${VERSIO}_${arq}.deb"
    info "Fet: packaging/dist/markdown-styler_${VERSIO}_${arq}.deb"
}

# --------------------------------------------------------------- .rpm ------
paquet_rpm() {
    comprova_eina rpmbuild
    [ -d "$DIST/markdown-styler" ] || construeix_bundle

    local rpmdir="$BUILD/rpm"
    info "Munte el paquet .rpm"
    rm -rf "$rpmdir"
    mkdir -p "$rpmdir/SOURCES/icons" "$rpmdir/SPECS" "$rpmdir/payload"

    cp -a "$DIST/markdown-styler/." "$rpmdir/payload/"
    tar -czf "$rpmdir/SOURCES/payload.tar.gz" -C "$rpmdir/payload" .
    install -m644 packaging/markdown-styler.desktop "$rpmdir/SOURCES/"
    install -m644 packaging/com.github.PauPedreguer.MarkdownStyler.appdata.xml \
        "$rpmdir/SOURCES/"
    install -m644 LICENSE THIRD-PARTY.md "$rpmdir/SOURCES/"

    local mida
    for mida in 16 24 32 48 64 128 256 512; do
        cp "$ICONES/${mida}x${mida}.png" "$rpmdir/SOURCES/icons/"
    done
    sed "s/@VERSIO@/$VERSIO/g" packaging/rpm/markdown-styler.spec \
        >"$rpmdir/SPECS/markdown-styler.spec"

    rpmbuild -bb --quiet --define "_topdir $rpmdir" \
        "$rpmdir/SPECS/markdown-styler.spec"

    mkdir -p "$SAIDA"
    rm -f "$SAIDA"/*.rpm
    cp "$rpmdir/RPMS/x86_64/"*.rpm "$SAIDA/"
    info "Fet: l'RPM és a packaging/dist"
}

# --------------------------------------------------------------- AppImage --
paquet_appimage() {
    [ -d "$DIST/markdown-styler" ] || construeix_bundle

    local appdir="$BUILD/AppDir" eina="$BUILD/tools/appimagetool-x86_64.AppImage"
    info "Munte l'AppImage"
    rm -rf "$appdir"
    omple_fhs "$appdir"

    install -m755 packaging/AppRun "$appdir/AppRun"
    install -m644 packaging/markdown-styler.desktop "$appdir/markdown-styler.desktop"
    cp "$ICONES/256x256.png" "$appdir/markdown-styler.png"
    # Llicència i components al costat de l'AppRun, on es veuen sense buscar.
    install -m644 LICENSE THIRD-PARTY.md "$appdir/"

    if [ ! -x "$eina" ]; then
        if [ "${SENSE_XARXA:-0}" = "1" ]; then
            mor "SENSE_XARXA=1 i falta appimagetool"
        fi
        info "Baixe appimagetool"
        mkdir -p "$BUILD/tools"
        curl -fL --retry 3 -o "$eina" \
            "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" \
            || mor "no s'ha pogut baixar appimagetool"
        chmod +x "$eina"
    fi

    mkdir -p "$SAIDA"
    # --no-appstream: la validació d'AppStream es fa a banda amb
    # «appstreamcli validate --no-net» (i no depén de si GitHub respon).
    ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 \
        "$eina" --appimage-extract-and-run --no-appstream "$appdir" \
        "$SAIDA/MarkdownStyler-${VERSIO}-x86_64.AppImage" \
        || mor "appimagetool ha fallat"
    chmod +x "$SAIDA/MarkdownStyler-${VERSIO}-x86_64.AppImage"
    info "Fet: packaging/dist/MarkdownStyler-${VERSIO}-x86_64.AppImage"
}

# ------------------------------------------------- icona d'escriptori ----
# Instal·la una entrada al menú d'aplicacions (i, si es vol, a l'escriptori)
# per a l'usuari actual. No calen permisos de root ni instal·lar el paquet:
# és la manera de tindre icona quan s'executa des del codi font o amb
# l'AppImage.
DADES_USUARI="${XDG_DATA_HOME:-$HOME/.local/share}"
APPS_USUARI="$DADES_USUARI/applications"
ICONES_USUARI="$DADES_USUARI/icons/hicolor"
NOM_LLANCADOR="markdown-styler.desktop"


# Directori d'escriptori de l'usuari (a Ubuntu en català és ~/Escriptori).
directori_escriptori() {
    local dir="" candidat
    if command -v xdg-user-dir >/dev/null 2>&1; then
        dir=$(xdg-user-dir DESKTOP 2>/dev/null || true)
    fi
    if [ -z "$dir" ] || [ "$dir" = "$HOME" ] || [ ! -d "$dir" ]; then
        for candidat in "$HOME/Escriptori" "$HOME/Desktop"; do
            if [ -d "$candidat" ]; then
                printf '%s\n' "$candidat"
                return 0
            fi
        done
        dir="$HOME/Desktop"
    fi
    printf '%s\n' "$dir"
}


# Copia la icona a ~/.local/share/icons/hicolor: el SVG (escalable) i els PNG
# que ja s'hagen generat amb «./build.sh icones».
installa_icones_usuari() {
    install -Dm644 assets/markdown-styler.svg \
        "$ICONES_USUARI/scalable/apps/markdown-styler.svg"
    local png mida
    for png in "$ICONES"/*.png; do
        [ -f "$png" ] || continue
        mida=$(basename "$png" .png)          # p. ex. 128x128
        install -Dm644 "$png" "$ICONES_USUARI/$mida/apps/markdown-styler.png"
    done
}


refresca_caches() {
    command -v update-desktop-database >/dev/null 2>&1 \
        && update-desktop-database "$APPS_USUARI" >/dev/null 2>&1 || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 \
        && gtk-update-icon-cache -f -t "$ICONES_USUARI" >/dev/null 2>&1 || true
}


# Escriu el .desktop. $1 destí, $2 executable, $3 directori de treball.
escriu_llancador() {
    local desti=$1 executable=$2 directori=$3
    {
        printf '[Desktop Entry]\n'
        printf 'Type=Application\n'
        printf 'Version=1.0\n'
        printf 'Name=Markdown Styler\n'
        printf 'GenericName=Generador de documents\n'
        printf 'Comment=Genera documents HTML i PDF amb estil a partir de fitxers Markdown\n'
        printf 'Exec="%s"\n' "$executable"
        [ -n "$directori" ] && printf 'Path=%s\n' "$directori"
        # TryExec no admet cometes: només té sentit si la ruta no té espais.
        case "$executable" in
            *" "*) ;;
            *) printf 'TryExec=%s\n' "$executable" ;;
        esac
        printf 'Icon=markdown-styler\n'
        printf 'Terminal=false\n'
        printf 'Categories=Office;\n'
        printf 'Keywords=markdown;pandoc;pdf;html;documents;\n'
        printf 'StartupNotify=true\n'
        printf 'StartupWMClass=markdown-styler\n'
    } > "$desti"
    chmod 755 "$desti"
    if command -v desktop-file-validate >/dev/null 2>&1; then
        desktop-file-validate "$desti" \
            || avis "el llançador no passa desktop-file-validate"
    fi
}


escriptori() {
    local mode="" tambe_escriptori=0 elimina=0 candidat
    while [ $# -gt 0 ]; do
        case "$1" in
            --codi)       mode="codi" ;;
            --appimage)   mode="appimage" ;;
            --escriptori) tambe_escriptori=1 ;;
            --elimina)    elimina=1 ;;
            *) mor "opció desconeguda per a «escriptori»: $1
       Valen --codi, --appimage, --escriptori i --elimina" ;;
        esac
        shift
    done

    local escriptori_dir fitxer
    escriptori_dir=$(directori_escriptori)
    fitxer="$APPS_USUARI/$NOM_LLANCADOR"

    if [ "$elimina" -eq 1 ]; then
        rm -f "$fitxer" "$escriptori_dir/$NOM_LLANCADOR"
        rm -f "$ICONES_USUARI/scalable/apps/markdown-styler.svg"
        rm -f "$ICONES_USUARI"/*/apps/markdown-styler.png
        refresca_caches
        info "Icona de Markdown Styler eliminada"
        return 0
    fi

    local appimage=""
    for candidat in "$SAIDA"/*.AppImage; do
        [ -f "$candidat" ] && appimage=$candidat
    done

    # Per defecte, l'arbre de codi font (sempre al dia) si hi ha entorn
    # virtual; si no, l'AppImage que hi haja a packaging/dist.
    if [ -z "$mode" ]; then
        if [ -x ".venv/bin/python" ] && [ -x "$ARREL_PROJECTE/run.sh" ]; then
            mode="codi"
        elif [ -n "$appimage" ]; then
            mode="appimage"
        else
            mode="codi"
        fi
    fi

    local executable directori
    case "$mode" in
        codi)
            [ -x "$ARREL_PROJECTE/run.sh" ] || mor "no hi ha run.sh executable"
            executable="$ARREL_PROJECTE/run.sh"
            directori="$ARREL_PROJECTE"
            if [ ! -x ".venv/bin/python" ]; then
                avis "no hi ha .venv/bin/python: run.sh usarà el python3 del sistema"
            fi
            ;;
        appimage)
            [ -n "$appimage" ] \
                || mor "no hi ha cap AppImage; feu abans «./build.sh appimage»"
            executable="$appimage"
            directori="$HOME"
            ;;
    esac

    mkdir -p "$APPS_USUARI"
    installa_icones_usuari
    escriu_llancador "$fitxer" "$executable" "$directori"

    if [ "$tambe_escriptori" -eq 1 ]; then
        mkdir -p "$escriptori_dir"
        install -m755 "$fitxer" "$escriptori_dir/$NOM_LLANCADOR"
        # El GNOME només executa els llançadors de l'escriptori si estan
        # marcats com a de confiança.
        command -v gio >/dev/null 2>&1 \
            && gio set "$escriptori_dir/$NOM_LLANCADOR" metadata::trusted true \
                >/dev/null 2>&1 || true
    fi

    refresca_caches
    info "Icona instal·lada: $fitxer"
    printf '    Exec: %s\n' "$executable"
    if [ "$tambe_escriptori" -eq 1 ]; then
        printf '    Escriptori: %s\n' "$escriptori_dir/$NOM_LLANCADOR"
    fi
    printf '    Cerca «Markdown Styler» al menú d'\''aplicacions.\n'
}


# --------------------------------------------------------------- ordres ----
neteja() {
    info "Esborre packaging/build i packaging/dist"
    rm -rf "$BUILD" "$SAIDA"
}

objectiu=${1:-all}
case "$objectiu" in
    deb|rpm|appimage|all) mkdir -p "$SAIDA" ;;
esac

case "$objectiu" in
    dir)
        construeix_bundle
        info "Fet: packaging/build/dist/markdown-styler/markdown-styler"
        ;;
    deb)
        paquet_deb
        ;;
    rpm)
        paquet_rpm
        ;;
    appimage)
        paquet_appimage
        ;;
    all)
        [ "$(uname -s)" = "Linux" ] \
            || mor "«all» només val a Linux; al Windows feu «dir» i després iscc"
        construeix_bundle
        paquet_deb
        paquet_rpm
        paquet_appimage
        ;;
    icones)
        prepara_venv
        genera_icones
        ;;
    escriptori)
        shift || true
        escriptori "$@"
        ;;
    clean)
        neteja
        ;;
    *)
        mor "objectiu desconegut: $objectiu
       (dir|deb|rpm|appimage|all|icones|escriptori|clean)"
        ;;
esac

if [ "$objectiu" != "clean" ] && [ "$objectiu" != "escriptori" ] \
    && [ -d "$SAIDA" ]; then
    printf '\nFitxers generats a packaging/dist:\n'
    ls -lh "$SAIDA"
fi
