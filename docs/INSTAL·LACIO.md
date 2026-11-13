# Instal·lació de Markdown Styler

Guia per a instal·lar l'aplicació a partir dels paquets publicats a
[Releases](https://github.com/PauPedreguer/MarkdownStyler/releases).
Els paquets porten **tot el que cal** (Python, PyQt6 i Pandoc): no cal
instal·lar res més.

## 1. Descarrega el paquet del teu sistema

| Sistema | Fitxer |
|---------|--------|
| Debian, Ubuntu, Linux Mint | `markdown-styler_1.0.0_amd64.deb` |
| Fedora, openSUSE | `markdown-styler-1.0.0-1.x86_64.rpm` |
| Qualsevol Linux (sense instal·lar) | `MarkdownStyler-1.0.0-x86_64.AppImage` |
| Windows 10/11 | `MarkdownStyler-1.0.0-setup.exe` |

## 2. Comprova la descàrrega (recomanat)

Cada versió publica un fitxer `SHA256SUMS` amb els binaris d'eixa versió:

```bash
sha256sum -c SHA256SUMS
```

A Windows, ho pots comprovar amb PowerShell:

```powershell
Get-FileHash .\MarkdownStyler-1.0.0-setup.exe -Algorithm SHA256
```

## 3. Instal·la

### Debian, Ubuntu, Linux Mint

```bash
sudo apt install ./markdown-styler_1.0.0_amd64.deb
```

`apt` resol tot sol les biblioteques del sistema que necessita Qt. Si el fas
servir per a generar PDF, instal·la també un navegador basat en Chromium (el
paquet el recomana, però no l'obliga):

```bash
sudo apt install chromium
```

### Fedora

```bash
sudo dnf install ./markdown-styler-1.0.0-1.x86_64.rpm
sudo dnf install chromium      # opcional, només per al PDF
```

### openSUSE

```bash
sudo zypper install ./markdown-styler-1.0.0-1.x86_64.rpm
```

### AppImage (sense instal·lar res)

```bash
chmod +x MarkdownStyler-1.0.0-x86_64.AppImage
./MarkdownStyler-1.0.0-x86_64.AppImage
```

Si el sistema no té FUSE 3, es pot executar sense muntar-lo:

```bash
./MarkdownStyler-1.0.0-x86_64.AppImage --appimage-extract-and-run
```

L'AppImage fa servir el navegador que tinga el sistema per al PDF.

#### Icona al menú (opcional)

L'AppImage no s'instal·la: si vols obrir-lo des del menú o de l'escriptori,
el camí més fàcil és [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher)
o Gear Lever. També ho pots fer a mà:

```bash
mkdir -p ~/Aplicacions
mv MarkdownStyler-1.0.0-x86_64.AppImage ~/Aplicacions/
cd ~/Aplicacions
./MarkdownStyler-1.0.0-x86_64.AppImage --appimage-extract markdown-styler.png
mv squashfs-root/markdown-styler.png . && rm -rf squashfs-root
```

I un fitxer `~/.local/share/applications/markdown-styler.desktop` amb els
teus camins:

```ini
[Desktop Entry]
Type=Application
Name=Markdown Styler
Comment=Genera documents HTML i PDF amb estil a partir de fitxers Markdown
Exec=/home/usuari/Aplicacions/MarkdownStyler-1.0.0-x86_64.AppImage
Icon=/home/usuari/Aplicacions/markdown-styler.png
Terminal=false
Categories=Office;
StartupWMClass=markdown-styler
```

Si tens el codi font, `./build.sh escriptori --appimage --escriptori` ho fa
tot sol (i `--elimina` ho desfà).

### Windows 10/11

1. Executa `MarkdownStyler-1.0.0-setup.exe`.
2. Si Windows SmartScreen avisa que l'editor és desconegut, tria **Més
   informació → Executa de totes maneres**: el binari no porta firma de codi.
3. L'instal·lador crea l'entrada al menú d'inici i, si ho tries, una icona a
   l'escriptori.

Per a generar PDF, Microsoft Edge (que ja ve instal·lat) és suficient.

## 4. On es desen les dades

La configuració del centre i els estils, plantilles i scripts que importes
**no** viuen dins del programa (que és de només lectura), sinó a:

- **Linux**: `~/.local/share/MarkdownStyler/`
- **Windows**: `%APPDATA%\MarkdownStyler\`

```
~/.local/share/MarkdownStyler/
├── config/institut.json
├── styles/
├── templates/
└── scripts/
```

La primera vegada es crea `config/institut.json` a partir de l'exemple que
porta l'aplicació (`config/institut.exemple.json`): nom, logo, professor,
departament i els colors d'identitat s'editen des de **⚙️ Configuració**.

Per a desar les dades a un altre lloc (per exemple, en una memòria USB), es pot
canviar l'arrel amb la variable d'entorn `MARKDOWN_STYLER_DATA`:

```bash
MARKDOWN_STYLER_DATA=/media/usb/markdown-styler ./markdown-styler
```

## 5. Comprovacions ràpides

```bash
markdown-styler --version    # ha de dir: Markdown Styler 1.0.0 (GPL-3.0-or-later)
markdown-styler --pdf document.md --out ~/Documents
```

## 6. Desinstal·lar

```bash
# Debian/Ubuntu
sudo apt remove markdown-styler

# Fedora
sudo dnf remove markdown-styler

# Windows: Configuració → Aplicacions → Markdown Styler → Desinstal·la
```

Desinstal·lar no esborra `~/.local/share/MarkdownStyler` (les teues dades):
esborra eixa carpeta a mà si ja no les vols.

## 7. Problemes freqüents

**No arranca i mostra un error sobre `xcb` o `libxcb-cursor`.**
Falten biblioteques de Qt al sistema. A Debian/Ubuntu:

```bash
sudo apt install libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0
```

**El botó d'imprimir o `--pdf` no genera res.**
Cal un navegador basat en Chromium al PATH (`chromium`, `chromium-browser`,
`google-chrome`, `chrome`, `brave-browser` o `microsoft-edge`). L'error ix a la
terminal amb el detall.

**L'AppImage no arranca en un servidor o contenidor.**
Pot ser que no hi haja FUSE 3. Prova `--appimage-extract-and-run` o fes servir
el `.deb`/`.rpm`.

**Les fòrmules matemàtiques no es veuen.**
Pandoc les renderitza amb KaTeX des d'un CDN: cal connexió a Internet en obrir
el document.

## 8. Compilar-ho un mateix

Si preferixes construir els paquets des del codi font:

```bash
git clone https://github.com/PauPedreguer/MarkdownStyler.git
cd MarkdownStyler
./build.sh all            # .deb, .rpm i AppImage a packaging/dist/
./build.sh escriptori     # i una icona al menú per a l'usuari actual
```

Detalls a [packaging/README.md](../packaging/README.md).

L'instal·lador de Windows no es pot creuar des de Linux: es genera en Windows
amb [Inno Setup 6](https://jrsoftware.org/isdl.php) (`./build.sh dir` des de Git
Bash i després `iscc packaging\windows\markdown-styler.iss`), o automàticament
amb el workflow de GitHub Actions en pujar l'etiqueta. El mateix workflow es pot
llançar a mà (*Run workflow*) per a comprovar la compilació sense publicar cap
versió.
