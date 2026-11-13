# Components de tercers

Markdown Styler es distribuïx sota la **GNU General Public License, versió 3 o
posterior** (GPL-3.0-or-later). Vegeu [LICENSE](LICENSE).

Els binaris publicats a *Releases* (`.deb`, `.rpm`, `.AppImage` i l'instal·lador
de Windows) inclouen els components següents. Tots són compatibles amb la
GPL-3.0: cap no imposa restriccions addicionals sobre el conjunt.

## Inclosos als binaris

| Component | Versió | Llicència | Ús al projecte |
|-----------|--------|-----------|----------------|
| [PyQt6](https://pypi.org/project/PyQt6/) | 6.11 | GPL-3.0-only | Interfície gràfica (bindings Python de Qt) |
| [Qt 6](https://www.qt.io/) | 6.11 | LGPL-3.0-only (opció triada) | Biblioteques de la interfície |
| [Python](https://www.python.org/) | 3.12 | PSF-2.0 | Intèrpret empaquetat amb l'aplicació |
| [Pandoc](https://pandoc.org/) | 3.14 | GPL-2.0-or-later | Conversió de Markdown a HTML |
| [PyInstaller](https://pyinstaller.org/) | 6.16 | GPL-2.0-or-later amb excepció del *bootloader* | Empaquetat de l'executable |

## Eines de compilació (no es distribuïxen)

| Eina | Llicència | Ús |
|------|-----------|----|
| [appimagetool](https://github.com/AppImage/appimagetool) | MIT | Genera l'AppImage |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | Llicència pròpia (llicència lliure per a programari lliure) | Genera l'instal·lador `.exe` |
| [rpmbuild](https://rpm.org/) | GPL-2.0-or-later | Genera el paquet `.rpm` |
| [dpkg-deb](https://wiki.debian.org/Teams/Dpkg) | GPL-2.0-or-later | Genera el paquet `.deb` |

## Recursos no empaquetats

El mode presentació i el suport de matemàtiques s'obtenen de Pandoc:

- `--katex` fa que Pandoc enllaçe **KaTeX** (MIT) des d'un CDN, igual que el
  CSS de les fonts. No s'inclou cap fitxer de KaTeX ni cap font al paquet; per
  això les fórmules necessiten connexió a Internet (o esperar la versió offline
  prevista).
- El ressaltat de codi el fa **skylighting** (dins de Pandoc, GPL-2.0-or-later)
  amb els temes de `themes/`, que són obra del projecte.

## Compliment de la LGPL (Qt)

La LGPL-3.0 exigeix que l'usuari puga substituir les biblioteques de Qt. Als
binaris, Qt viatja com a biblioteques compartides separades de l'executable:

- **Linux**: `_internal/PyQt6/Qt6/lib/*.so.*` (AppImage i `.deb`/`.rpm`) — es
  poden substituir per una versió compatible.
- **Windows**: `_internal/PyQt6/Qt6/bin/*.dll`.

L'executable de Python (PyInstaller) no enllaça Qt de manera estàtica: carrega
les `.so`/`.dll` anteriors en temps d'execució.

## Codi font

La GPL-3.0 obliga a oferir el codi font corresponent a qui reba un binari. El
codi font complet de cada versió publicada és al repositori:

<https://github.com/PauPedreguer/MarkdownStyler>

i a la mateixa pàgina de *Releases*, amb l'etiqueta de la versió corresponent
(per exemple `v1.0.0`).
