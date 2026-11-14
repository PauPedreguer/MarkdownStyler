# Markdown Styler

Aplicació d'escriptori (PyQt6) que genera documents HTML i PDF amb estil professional a partir de fitxers Markdown, utilitzant **Pandoc** com a motor de conversió.

## ☕ Suporta el projecte

Markdown Styler és gratuït, no recull cap dada i el codi és obert
(GPL-3.0-or-later). Si t'ha estalviat temps i vols convidar-me a un cafè:

[![Convida'm a un cafè](https://img.shields.io/badge/%E2%98%95-Convida%27m%20a%20un%20caf%C3%A8-1d4ed8)](https://buymeacoffee.com/paupedreguer)

Les donacions són voluntàries: no donen dret a suport prioritari ni a cap
funcionalitat extra.

## ✨ Característiques

- 🎨 **Colors d'identitat**: cada color de la finestra va lligat al seu curs i a la seua assignatura, i s'editen des de Configuració en una taula (`Color | Curs | Assignatura`).
- 📄 **Documents HTML i PDF**: genera l'HTML amb portada, sumari i estil professional; el PDF s'obté imprimint-lo des del navegador (botó 🖨️ del document o `./pdf.sh`).
- 🏫 **Configuració de l'institut**: nom, logo, professor i departament; el curs i l'assignatura viuen a la taula de colors.
- 🎯 **Ressaltat de codi**: el genera Pandoc (`--highlight-style`) amb temes propis (`themes/one-dark.theme`, Material Ocean i GitHub Dark) afinats per al fons fosc del bloc i per als llenguatges de classe (kotlin, java, bash, html, css, javascript, c++, c#, php…). Sense llibreries externes.
- 📥 **Arrossega i deixa anar**: suport per arrossegar fitxers `.md` directament a la finestra.
- 🧩 **Plantilles i estils personalitzables**: importa els teus propis CSS, plantilles HTML i scripts JS.

## 📥 Descarrega

Els paquets preparats es publiquen a
[**Releases**](https://github.com/PauPedreguer/MarkdownStyler/releases). Porten
**tot inclòs** (Python, PyQt6 i Pandoc): no cal instal·lar res més.

| Sistema | Fitxer | Instal·lació |
|---------|--------|--------------|
| Debian, Ubuntu, Linux Mint | `markdown-styler_1.0.0_amd64.deb` | `sudo apt install ./markdown-styler_1.0.0_amd64.deb` |
| Fedora, openSUSE | `markdown-styler-1.0.0-1.x86_64.rpm` | `sudo dnf install ./markdown-styler-1.0.0-1.x86_64.rpm` |
| Qualsevol Linux, sense instal·lar | `MarkdownStyler-1.0.0-x86_64.AppImage` | `chmod +x` i doble clic |
| Windows 10/11 | `MarkdownStyler-1.0.0-setup.exe` | Executa l'instal·lador |

> Per a generar PDF cal un navegador basat en Chromium: a Linux, `chromium` (els
> paquets `.deb`/`.rpm` el recomanen); a Windows n'hi ha prou amb Microsoft
> Edge, que ja ve instal·lat.

Cada versió publica també un fitxer `SHA256SUMS` per a comprovar que la
descàrrega no s'ha fet malbé:

```bash
sha256sum -c SHA256SUMS
```

La guia completa (dependències de cada distribució, FUSE, desinstal·lació i
problemes freqüents) és a **[docs/INSTAL·LACIO.md](docs/INSTAL·LACIO.md)**.

## 📁 Estructura del projecte

```
MarkdownStyler/
├── main.py                    # Punt d'entrada (GUI o --pdf)
├── src/                       # Codi font (arquitectura per capes)
│   ├── core/                  # Models de domini
│   │   ├── curs.py            # Càlcul del curs acadèmic
│   │   ├── identitats.py      # Colors d'identitat (color + curs + assignatura)
│   │   └── models.py          # ExportOptions (dataclass)
│   ├── use_cases/             # Casos d'ús de l'aplicació
│   │   └── generate_html.py   # Lògica d'exportació
│   ├── infrastructure/        # Infraestructura (Pandoc, config, rutes)
│   │   ├── config_repo.py     # Càrrega/desat de configuració
│   │   ├── highlight_styles.py# Temes de ressaltat (--highlight-style)
│   │   ├── pandoc_converter.py# Invocació de Pandoc
│   │   └── project_paths.py   # Recursos del paquet i dades de l'usuari
│   ├── version.py             # Versió i llicència (main.py --version)
│   └── ui/                    # Interfície d'usuari (PyQt6)
│       ├── app.py             # Finestra principal
│       ├── style.qss          # Estils de la UI
│       └── components/        # Components reutilitzables (Configuració, etc.)
├── tests/                     # Tests unitaris
│   ├── test_models.py
│   ├── test_curs.py
│   ├── test_config_repo.py
│   ├── test_project_paths.py
│   ├── test_generate_html.py
│   ├── test_pandoc_converter.py
│   ├── test_highlight_styles.py # Temes de ressaltat: JSON, contrast i rutes
│   ├── test_templates.py      # Invariants de plantilla/JS de l'HTML generat
│   ├── test_pdf_script.py     # PDF de punta a punta (es salta sense Chromium)
│   ├── test_presentacio_html.py # Mode presentació en un navegador real
│   ├── test_ui.py             # Helpers d'UI (sense QApplication)
│   └── test_identitats.py     # Colors d'identitat: neteja, presets i etiquetes
├── config/                    # institut.exemple.json (la configuració real viu a les dades de l'usuari)
├── templates/                 # Plantilles HTML de Pandoc
├── styles/                    # base.css, prova.css i presentacio.css
├── scripts/                   # script.js i presentacio.js
├── themes/                    # Temes de ressaltat propi (JSON de pandoc)
├── assets/                    # Recursos estàtics (logos, icones, imatges)
├── examples/                  # Documents de prova (només les fonts .md)
├── packaging/                 # Empaquetat: .deb, .rpm, AppImage i instal·lador .exe
├── docs/                      # Guia d'instal·lació per a usuaris
├── run.sh                     # Llançador (usa el .venv local)
├── pdf.sh                     # Markdown -> PDF amb Chromium headless
├── build.sh                   # Paquets (deb|rpm|appimage|all) i icona d'escriptori
├── requirements.txt           # Dependències de Python
├── LICENSE                    # GPL-3.0-or-later (text complet)
├── THIRD-PARTY.md             # Llicències dels components de tercers
└── pyproject.toml             # Configuració del projecte i pytest
```

> **`examples/`** conté documents de prova (`demo.md`, `Examen Linux.md`) que
> exerciten títols, llistes niuades, tasques, taules, blocs de codi i imatges.
> Les eixides `.html`/`.pdf` **no es versionen**: es generen amb l'aplicació.

## 🚀 Instal·lació des del codi font

> Si només vols l'aplicació, ves a [Descarrega](#-descarrega): els paquets ja
> porten Python, PyQt6 i Pandoc.

### Requisits previs

- **Python 3.10+**
- **Pandoc** instal·lat i disponible al PATH (si el projecte té `bin/pandoc`,
  s'usa eixe abans que el del sistema)
- **Chromium o Google Chrome** (només per a generar PDF amb `pdf.sh`)

### Instal·lació de dependències

```bash
pip install -r requirements.txt
```

O bé, amb el gestor de paquets:

```bash
pip install -e ".[dev]"
```

## ▶️ Execució

```bash
python main.py        # o ./run.sh: obri la interfície gràfica
```

### 🖱️ Icona al menú o a l'escriptori

Si executes des del codi font (o amb l'AppImage) i vols obrir l'aplicació
fent clic a una icona, instal·la el llançador per a l'usuari actual:

```bash
./build.sh escriptori               # icona al menú que executa ./run.sh
./build.sh escriptori --escriptori  # a més, un access directe a l'escriptori
./build.sh escriptori --appimage    # la icona executa l'AppImage de packaging/dist
./build.sh escriptori --elimina     # lleva la icona
```

No cal `sudo`: escriu a `~/.local/share/applications/markdown-styler.desktop` i
copia la icona a `~/.local/share/icons/hicolor/`. Els paquets `.deb`, `.rpm` i
el `.exe` ja creen la icona en instal·lar-se.

L'aplicació genera **HTML**. El **PDF** s'obté imprimint eixe HTML, de manera
que la maquetació (portada, índex, capçaleres, número de pàgina) ve de les
regles `@page` de `styles/prova.css` i la renderitza el navegador.

### 📄 Generar el PDF

1. **Des del document**: obri l'HTML generat i prem el botó **🖨️ Imprimir
   pràctica** de la barra lateral (o `Ctrl+P`) i tria «Desa com a PDF».
2. **Des de la línia d'ordres** (Chromium headless):

```bash
./pdf.sh practica.md                # deixa el PDF al costat del .md
./pdf.sh practica.md ~/Documents    # o a la carpeta que indiques
```

Equival a:

```bash
python main.py --pdf practica.md --out ~/Documents --title "Pràctica 1"
```

`pdf.sh` detecta el navegador instal·lat (`chromium`, `chromium-browser`,
`google-chrome`, `google-chrome-stable`, `chrome`, `brave-browser` o
`microsoft-edge`). El PDF resultant inclou portada, índex, capçalera amb les
dades de l'institut i el peu «Pàgina X de Y» (llevat de la portada).

## 🌗 Tema clar i fosc

El tema és **un de sol per a tot el document**: el mateix que veus en pantalla
és el que veuràs en entrar en mode presentació, i el canvi es recorda.

- **Botó ☾** de la fila flotant de la dreta (canvia a ☀ quan està fosc) o la
  tecla `T`. També funciona dins de la presentació.
- La preferència es desa al navegador (`localStorage`), de manera que es
  manté en tornar a obrir el fitxer. El primer colp s'aplica el tema inicial
  de *Configuració → Presentació* (per defecte, clar).
- El tema s'aplica **abans del primer pintat**, així que no hi ha flaix
  clar→fosc en carregar.
- El **PDF ix sempre en clar**: la paleta fosca viu només en pantalla
  (`@media print` la desactiva), de manera que imprimir o desar a PDF no
  canvia res.

Els colors ixen de `styles/base.css` (`:root` per al clar i `html.tema-fosc`
per al fosc). Els estils triables no han de definir colors propis: usen les
variables (`--color-fons`, `--color-superficie`, `--color-text`,
`--color-acent`, `--mescla-fons`…) i hereten el tema automàticament.

## 🖥️ Mode presentació

El **mateix HTML** que genera l'aplicació es pot projectar com una
presentació, sense escriure cap marcador especial al Markdown: no calen
`---` ni cap `#` de diapositiva.

- **Des de l'aplicació**: el botó **▶ Presentar** del diàleg d'exportació
  (obri el fitxer acabat de generar ja en mode presentació).
- **Des del document**: el botó **▶** de la fila flotant de la dreta (davant de
  ⛶ pantalla completa, ☾ tema i ⌃ capçalera) o les tecles `P` / `F5`.

En activar-se, el document no es clona: es re-agrupa sobre la marxa i, en
eixir, es restaura exactament com era. Els diagrames de mermaid, les fórmules
de KaTeX, el codi amb el seu botó de còpia i els enllaços del sumari continuen
funcionant.

Al peu hi ha el comptador `n / total` i quatre botons d'icona: **◀ ▶**
(navegar), **?** (ajuda) i **✕** (eixir). El **tema** (☾/☀) i la **pantalla
completa** (⛶) no es repetixen ahí: continuen a la cantonada superior dreta,
com en la resta del document.

### Diapositives o scroll

- **Diapositives** (per defecte): cada encapçalament `##` obri una
  diapositiva. El títol va centrat, com una capçalera, perquè no es confonga
  amb els apartats del cos. Si una secció no cap en una pantalla, es dividix
  tota sola: talla per blocs sencers davant d'un encapçalament, de manera que
  el títol de l'apartat i el seu contingut passen junts i **cap títol no es
  queda sol** al final d'una diapositiva. Mai talla una taula, un bloc de codi
  o una figura pel mig; si un bloc és més gran que la pantalla (o no hi ha cap
  tall net), la diapositiva fa scroll intern i mostra «↓ continua».
- **Scroll**: les seccions no es fragmenten ni es tanquen a una pantalla; es
  recorre el document sencer sense parades, que és el que fa falta per a
  llegir. Ací `↓` `↑` i `Re Pàg` `Av Pàg` mouen la pàgina poc a poc (un quart
  o una pantalla) i mai no salten text, i `→` `Espai` `←` porten a l'inici de
  la secció següent o anterior.

El mode es pot canviar **en directe** amb la tecla `M` (no té botó al peu: el
mode habitual es tria a la configuració), i el nivell de títol que obri cada
diapositiva es tria a *Configuració → Presentació* (`#`, `##` o `###`).
El tema (`T` o el botó ☾) és el mateix del document: canviar-lo dins de la
presentació el canvia també a la vista normal, i a l'inrevés.

### Tecles

| Tecla | Acció |
| --- | --- |
| `→` `Espai` `Av Pàg` | Diapositiva o secció següent (si en queda, acaba de recórrer-la) |
| `←` `Re Pàg` | Anterior |
| `↓` `↑` | En mode diapositives, com `→` `←`; en mode scroll, mouen la pàgina poc a poc |
| `Re Pàg` `Av Pàg` | En mode scroll, una pantalla amunt o avall |
| `Inici` / `Fi` | Primera / última |
| `M` | Diapositives ↔ scroll |
| `F` | Pantalla completa |
| `T` | Tema clar ↔ fosc |
| `?` | Ajuda amb totes les tecles |
| `Esc` | Eixir (o tancar l'ajuda o la pantalla completa) |

La barra superior mostra el progrés, i el peu el comptador `n / total` i els
botons. La posició es desa al navegador i l'enllaç `…html#presentar/3` obri
directament la diapositiva 3. En imprimir (`Ctrl+P`) la presentació es
desactiva sola, de manera que el PDF ix igual que sempre.

## 🧪 Tests

Els tests utilitzen `unittest` (inclòs a Python) i `pytest`:

```bash
# Amb unittest
python -m unittest discover -s tests

# Amb pytest
pytest
```

## 🛠️ Arquitectura

El projecte segueix una **arquitectura per capes** (Clean Architecture simplificada):

- **`core/`**: models de domini purs, sense dependències externes.
- **`use_cases/`**: orquestra la lògica de negoci (exportació).
- **`infrastructure/`**: implementacions concretes (Pandoc, sistema de fitxers, config).
- **`ui/`**: capa de presentació (PyQt6).

Aquesta separació permet testar la lògica de negoci de manera aïllada, sense necessitat d'una interfície gràfica ni de Pandoc instal·lat.

## 🎨 Blocs de codi

El ressaltat el fa **Pandoc**: l'aplicació li passa un fitxer de tema propi
(`themes/*.theme`, format JSON de *skylighting*) afinat per al fons fosc del
bloc de codi (`#1e293b`) i per als colors de text de la resta del document.

A més, `scripts/script.js` completa el que Pandoc no pot saber. Pandoc treballa
amb expressions regulars i no té informació semàntica: en Kotlin, Java,
JavaScript, C++, C#, PHP o Python deixa sense color els identificadors que són
crides o tipus. El JS els marca amb la classe que els pertoca:

- `fu` (color de funció) si l'identificador va seguit de parèntesis:
  `Column(`, `Modifier.fillMaxSize()`, `println(`.
- `dt` (color de tipus) si comença amb majúscula i té alguna minúscula:
  `modifier: Modifier = Modifier` pinta els dos `Modifier` igual. Queden fora
  les constants (`MAX_SIZE`) i l'accés a un membre (`Arrangement.Center`).

Només actua en eixos llenguatges (no en HTML, CSS, bash ni SQL), no toca mai
els tokens que ja ha pintat Pandoc i no pinta les paraules clau que porten
parèntesi (`if (`, `return (`…).

Damunt de cada bloc hi ha una barra amb el nom del llenguatge i el botó de
copiar. Els blocs que Pandoc no ressalta (un bloc sense llenguatge, amb
l'etiqueta `text`, o amb un llenguatge que no coneix) no van embolcallats en el
`div.sourceCode` que porten els altres, així que `scripts/script.js` crea el
mateix contenidor: la barra ha de quedar sempre enganxada a la vora del bloc,
no dins del codi. L'etiqueta mostra el llenguatge que s'haja escrit (`FOOBAR`)
o `TEXT` si no se n'ha posat cap.

| Tema | Fitxer | Comentari |
|---|---|---|
| **One Dark** (recomanat) | `themes/one-dark.theme` | Paleta d'One Dark; tots els tokens amb contrast ≥ 4.5:1 |
| Material Ocean | `themes/material-ocean.theme` | Tons pastel, més suau |
| GitHub Dark | `themes/github-dark.theme` | Blau clar per a funcions i números |
| zenburn / espresso / breezedark / monochrome | (de Pandoc) | Els temes foscos que porta Pandoc |

Els temes **clars** de Pandoc (`pygments`, `tango`, `kate`, `haddock`) no
s'oferixen: sobre el bloc fosc deixen els tokens quasi negres i el codi sembla
d'un sol color.

Criteri de colors (els tres temes): la **puntuació** (`(`, `)`, `=`, `,`, `{`)
va en gris, perquè en cian tot el bloc sembla subratllat; els **paràmetres i
variables** van en el color del text, com a Android Studio; i el roig queda
reservat per a errors, alertes i preprocessador.

### Llenguatges dels blocs de codi

Posa l'etiqueta després de les tres cometes invertides:

````markdown
```kotlin
fun suma(a: Int, b: Int) = a + b
```
````

| Llenguatge | Etiqueta | Àlies |
|---|---|---|
| Kotlin | `kotlin` | |
| Java | `java` | |
| Bash / shell | `bash` | `sh`, `zsh` |
| HTML | `html` | |
| CSS | `css` | |
| JavaScript | `javascript` | `js` |
| TypeScript | `typescript` | `ts` |
| C++ | `c++` | `cpp` |
| C# | `c#` | `cs` |
| PHP | `php` | |
| Python | `python` | `py` |
| SQL | `sql` | |

> **Atenció amb el `#`**: si un títol conté una «almohadilla» (per exemple el
> llenguatge *C#*), Markdown la interpreta com un altre títol i el text queda
> tallat. Escriu-la escapada:
>
> ```markdown
> # C\#          -> mostra «C#»
> ## Pràctica de C\#
> ```
>
> Dins d'un bloc de codi no cal escapar res.

Per a afegir un tema propi: copia un fitxer de `themes/`, canvia-li els colors
i declara'l a `ESTILS_PROJECTE` de `src/infrastructure/highlight_styles.py`.

## 📝 Configuració

La configuració de l'institut es desa a:

- **Linux**: `~/.local/share/MarkdownStyler/config/institut.json` (o dins de
  `$XDG_DATA_HOME/MarkdownStyler/config/institut.json` si tens eixa variable);
- **Windows**: `%APPDATA%\MarkdownStyler\config\institut.json`.

El paquet instal·lat és de **només lectura** (AppImage, `/usr/lib`, `Program
Files`), i per això les dades viuen al directori de l'usuari. La primera vegada
es copia `config/institut.exemple.json` —el fitxer d'exemple que viatja amb
l'aplicació— i ja es pot editar des de Configuració o a mà. La variable
d'entorn `MARKDOWN_STYLER_DATA` canvia el directori sencer (mode portable).
Els CSS, les plantilles i els scripts que importes des de Configuració també
es desen ahí, no dins del paquet:

```
~/.local/share/MarkdownStyler/
├── config/institut.json
├── styles/meu-estil.css
├── templates/meua-plantilla.html
└── scripts/meu-script.js
```

L'estructura del JSON és esta:

```json
{
  "institut_nom": "IES Exemple",
  "institut_logo": "",
  "professor": "Nom i cognoms",
  "departament": "Departament",
  "identitats": [
    {"color": "#1d4ed8", "curs": "1r", "assignatura": "Assignatura"},
    {"color": "#166534", "curs": "", "assignatura": ""}
  ],
  "css_name": "prova.css",
  "template_name": "base.html",
  "js_name": "script.js",
  "highlight_style": "themes/one-dark.theme"
}
```

`institut_logo` pot quedar buit (`""`): aleshores la portada i la capçalera no
pinten cap imatge (no queda un `<img>` trencat).

`highlight_style` pot ser un tema propi (`themes/one-dark.theme`,
`themes/material-ocean.theme`, `themes/github-dark.theme`) o el nom d'un tema
fosc de Pandoc (`zenburn`, `espresso`, `breezedark`, `monochrome`).

`identitats` és la llista de colors de la finestra principal: cada color va
lligat al seu **curs** (el grup, p. ex. `1r DAW`) i a la seua **assignatura**
(p. ex. `LMSGI`). En triar un color, el document n'hereta el color i la
capçalera (i la portada del PDF) agafa eixes dades. El **primer color** de la
llista és el document per defecte: ix triat en obrir la finestra i és el que
s'usa si el color triat deixa el curs o l'assignatura buits.
No confongues `curs` (el grup) amb el curs acadèmic (l'any, p. ex. `26-27`), que
es tria a la finestra principal.

A la finestra principal els colors van en **una sola fila**: cada color és una
mostra rodona amb el seu curs i la seua assignatura davall. Si no hi caben,
la fila s'arrissa amb la barra horitzontal. El curs i l'assignatura no
s'editen ahí: ixen del color triat i es canvien a Configuració.

Els colors també es poden escriure **pel nom** (`Taronja`, `Verd`, `Blau`,
`Granat`, `Ocre`, `Lila`, `Teal`, `Groc`, `Roig`, `Rosa`, `Turquesa`, `Marró`,
`Negre`) en compte del hexadecimal:

```json
"identitats": [
  {"color": "Taronja", "curs": "1r DAW", "assignatura": "LMSGI"},
  {"color": "Verd", "curs": "2n DAW", "assignatura": "DWEC"}
]
```

Les dos formes (hexadecimal i nom) es poden combinar dins de la mateixa llista;
en desar des de la interfície sempre es guarda la forma completa
(`{"color": "#c2410c", "curs": "1r DAW", "assignatura": "LMSGI"}`).

Pots modificar aquests valors des de la interfície (botó **⚙️ Configuració**),
on els colors es poden afegir, editar i esborrar (sempre n'hi ha d'haver un), o
editant el fitxer directament.

### 🎨 Colors d'identitat des de Configuració

El diàleg de Configuració s'organitza en tres seccions —**INSTITUT** (nom,
logo, professor i departament), **COLORS D'IDENTITAT** i **CONFIGURACIÓ DE
DOCUMENTS**— dins d'una àrea amb scroll, amb el botó **Desar configuració**
sempre visible. La taula creix amb les files fins a sis; a partir d'ahí
s'arrissa, de manera que el diàleg no es fa més alt que la pantalla.

La secció **COLORS D'IDENTITAT** de Configuració té una taula amb una fila per
color i tres columnes: **Color**, **Curs** i **Assignatura**.

- **Color**: s'escriu el nom (`Taronja`) o un hexadecimal (`#c2410c`) i, si el
  nom és conegut, es queda escrit el nom. El quadret de la dreta obri el
  selector de color del sistema.
- **Curs** i **Assignatura**: quadres editables, amb una entrada buida i, com a
  suggeriment, els valors que ja hi ha a la taula; també se'n poden escriure de
  nous. Els dos camps són opcionals.
- **La primera fila** és el document per defecte: és el color que ix triat en
  obrir la finestra. Per a canviar-lo, mou la fila amb **Pujar**/**Baixar**.
- **Afegir**, **Esborrar**, **Pujar** i **Baixar** editen les files;
  **Colors per defecte** torna a omplir la taula amb la paleta de sempre.

En desar, la taula es convertix en la llista `identitats` del JSON. Si alguna
fila té un color que no es reconeix, o curs/assignatura sense color, no es desa
res i s'assenyalen les files perquè les corregisques (`fila 3: «verd clar» no és
un color conegut`); sempre ha de quedar almenys un color.

## 📜 Llicència

Markdown Styler es distribuïx sota la **GNU General Public License, versió 3 o
posterior** (GPL-3.0-or-later). El text complet és a [LICENSE](LICENSE) i les
llicències dels components que viatgen amb els binaris (PyQt6, Qt, Pandoc,
Python i PyInstaller) consten a [THIRD-PARTY.md](THIRD-PARTY.md).

La GPL obliga a oferir el codi font corresponent a qui rep un binari. Per això
cada versió publicada té el seu codi al repositori, amb l'etiqueta de la
versió (per exemple `v1.0.0`):

<https://github.com/PauPedreguer/MarkdownStyler>

Copyright © 2026 Pau Palacios Server
