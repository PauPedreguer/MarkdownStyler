# Empaquetat

Ací viu tot el que servix per a publicar binaris. L'única ordre que cal
recordar és `./build.sh` (a l'arrel del projecte):

```bash
./build.sh deb        # .deb     → packaging/dist/
./build.sh rpm        # .rpm     → packaging/dist/
./build.sh appimage   # AppImage → packaging/dist/
./build.sh all        # els tres (Linux)
./build.sh dir        # només el bundle de PyInstaller (per a proves)
./build.sh icones     # regenera les icones (packaging/build/icones)
./build.sh escriptori # icona al menú per a l'usuari actual
./build.sh clean      # esborra packaging/build i packaging/dist
```

`./build.sh escriptori` no genera cap paquet: instal·la el llançador a
`~/.local/share/applications/markdown-styler.desktop` i la icona a
`~/.local/share/icons/hicolor/`. Per defecte executa `./run.sh` (l'arbre de
codi font, sempre al dia); amb `--appimage` executa l'AppImage de
`packaging/dist`, i amb `--escriptori` també deixa un access directe a
l'escriptori. `--elimina` ho desfà.

La primera vegada crea un entorn virtual a `packaging/build/venv`, baixa
Pandoc a `packaging/build/cache` i genera les icones. No toca el `.venv` de
desenvolupament ni el Pandoc del sistema.

## Què s'empaqueta

| Peça | Origen | Destí al paquet |
|------|--------|-----------------|
| Executable i Python | PyInstaller (`markdown-styler.spec`) | `/usr/lib/markdown-styler/` |
| Pandoc | `packaging/build/arrel/bin/pandoc` | `/usr/lib/markdown-styler/bin/pandoc` |
| Estils, plantilles, scripts, temes | `styles/`, `templates/`, `scripts/`, `themes/` | `…/markdown-styler/` |
| Icones | `assets/markdown-styler.svg` → `packaging/build/icones` | `/usr/share/icons/hicolor/…` |
| Entrada de menú | `packaging/markdown-styler.desktop` | `/usr/share/applications/` |
| Metadades | `packaging/com.github.PauPedreguer.MarkdownStyler.appdata.xml` | `/usr/share/metainfo/` |
| Configuració d'exemple | `config/institut.exemple.json` | `…/markdown-styler/config/` |

`prepara_arbre()` copia el codi amb `tar --exclude`: **mai** no s'empaqueta
`config/institut.json` (la configuració real del centre) ni
`assets/logoIESPereMariaOrtsiBosch.png`, ni `.git`, `tests/` o `examples/`.

Les dades de l'usuari (configuració, CSS/plantilles/JS importats) es creen la
primera vegada que arranca l'aplicació a `~/.local/share/MarkdownStyler`
(o `%APPDATA%\MarkdownStyler`). Els paquets són de només lectura.

## Fitxers

```
packaging/
├── markdown-styler.spec          # PyInstaller (Linux i Windows)
├── make_icon.py                  # SVG → PNG (16…512) i .ico, amb PyQt6
├── AppRun                        # llançador de l'AppImage
├── markdown-styler.desktop       # entrada de menú
├── com.github.PauPedreguer.MarkdownStyler.appdata.xml   # metadades per a les botigues
├── deb/control.in                # plantilla del control de Debian
├── deb/copyright                 # copyright del paquet (DEP-5)
├── deb/postinst, deb/postrm      # actualitzen les caches del menú
├── rpm/markdown-styler.spec      # plantilla de l'RPM
└── windows/markdown-styler.iss   # Inno Setup (instal·lador .exe)
```

## Windows

El paquet de Windows és un `.exe` d'[Inno Setup 6](https://jrsoftware.org/isdl.php):
no es pot creuar des de Linux (PyInstaller no compila per a un altre sistema i
`iscc` només existix a Windows), de manera que **s'ha de generar en Windows**.
N'hi ha dos camins.

### Automàtic (el normal)

El workflow de GitHub Actions ho fa tot en un runner `windows-latest`:

```text
./build.sh dir                                # Git Bash del runner
iscc packaging\windows\markdown-styler.iss    # Inno Setup
```

I el job `publica` penja `packaging\dist\MarkdownStyler-<versió>-setup.exe` a la
Release amb la resta de paquets i el `SHA256SUMS`.

### A mà (pla B)

Si cal compilar-lo al teu PC (perquè la CI no està disponible o vols provar un
canvi) el resultat és el mateix. Cal **Git per a Windows** (Git Bash), Python
3.10+ i Inno Setup 6:

```bash
git clone https://github.com/PauPedreguer/MarkdownStyler.git
cd MarkdownStyler
git checkout v1.0.0                # el binari ha de nàixer de l'etiqueta (GPL)

PYTHON=python ./build.sh dir       # → packaging/build/dist/markdown-styler/
"/c/Program Files (x86)/Inno Setup 6/ISCC.exe" packaging/windows/markdown-styler.iss
gh release upload v1.0.0 packaging/dist/MarkdownStyler-1.0.0-setup.exe
```

`./build.sh dir` en Git Bash funciona perquè només usa `python -m venv`, `pip`,
`curl`, `tar`, `sed` i el `zipfile` de Python (`install`, que Git Bash no té,
només s'usa als objectius de Linux). També es pot pujar l'`.exe` arrossegant-lo
a la Release des del navegador.

Dos detalls que cal no oblidar:

- **`SHA256SUMS`**: si puges l'`.exe` després que la CI haja publicat, el fitxer
  de sumes es queda sense eixa línia. Regenera'l sencer:

  ```bash
  mkdir -p ~/release && cd ~/release
  gh release download v1.0.0
  rm -f SHA256SUMS
  sha256sum * > SHA256SUMS           # a Git Bash també hi és sha256sum
  gh release upload v1.0.0 SHA256SUMS --clobber
  ```

- **Versió**: ha de coincidir a `src/version.py`, `pyproject.toml`,
  `#define Versio` de `markdown-styler.iss` i la data de l'appdata.

## Publicació

`.github/workflows/release.yml` s'executa en pujar una etiqueta `v*`:

```bash
# 1. Canvia la versió a src/version.py (i a pyproject.toml)
# 2. Etiqueta i puja
git tag v1.0.0
git push origin v1.0.0
```

El workflow passa els tests, construïx els quatre paquets, genera
`SHA256SUMS` i els publica a *Releases* amb les notes generades
automàticament.

També es pot llançar a mà (*Run workflow*): en eixe cas **no publica res**,
només compila i deixa els quatre artefactes a la pàgina del run, cosa que servix
per a comprovar que la compilació de Windows funciona abans d'etiquetar.

> Si canvies la versió, actualitza també `packaging/windows/markdown-styler.iss`
> (`#define Versio`) i la data de `packaging/com.github.PauPedreguer.MarkdownStyler.appdata.xml`.
