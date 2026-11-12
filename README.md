# Markdown Styler

Aplicació d'escriptori (PyQt6) que genera documents HTML i PDF amb estil professional a partir de fitxers Markdown, utilitzant **Pandoc** com a motor de conversió.

## ✨ Característiques

- 🎨 **Personalització de colors**: presets de color d'identitat configurables.
- 📄 **Documents HTML i PDF**: genera l'HTML amb portada, sumari i estil professional; el PDF s'obté imprimint-lo des del navegador (botó 🖨️ del document o `./pdf.sh`).
- 🏫 **Configuració de l'institut**: nom, logo, curs, assignatura, professor i departament.
- 🎯 **Ressaltat de codi**: el genera Pandoc (`--highlight-style`) amb temes propis (`themes/one-dark.theme`, Material Ocean i GitHub Dark) afinats per al fons fosc del bloc i per als llenguatges de classe (kotlin, java, bash, html, css, javascript, c++, c#, php…). Sense llibreries externes.
- 📥 **Arrossega i deixa anar**: suport per arrossegar fitxers `.md` directament a la finestra.
- 🧩 **Plantilles i estils personalitzables**: importa els teus propis CSS, plantilles HTML i scripts JS.

## 📁 Estructura del projecte

```
MarkdownStyler/
├── main.py                    # Punt d'entrada (GUI o --pdf)
├── src/                       # Codi font (arquitectura per capes)
│   ├── core/                  # Models de domini
│   │   ├── curs.py            # Càlcul del curs acadèmic
│   │   └── models.py          # ExportOptions (dataclass)
│   ├── use_cases/             # Casos d'ús de l'aplicació
│   │   └── generate_html.py   # Lògica d'exportació
│   ├── infrastructure/        # Infraestructura (Pandoc, config, rutes)
│   │   ├── config_repo.py     # Càrrega/desat de configuració
│   │   ├── highlight_styles.py# Temes de ressaltat (--highlight-style)
│   │   ├── pandoc_converter.py# Invocació de Pandoc
│   │   └── project_paths.py   # Resolució de rutes del projecte
│   └── ui/                    # Interfície d'usuari (PyQt6)
│       ├── app.py             # Finestra principal
│       ├── style.qss          # Estils de la UI
│       └── components/        # Components reutilitzables
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
│   └── test_ui.py             # Helpers d'UI (sense QApplication)
├── config/                    # Configuració de l'institut (JSON)
├── templates/                 # Plantilles HTML de Pandoc
├── styles/                    # Fulls d'estil CSS
├── scripts/                   # Scripts JS per als documents generats
├── themes/                    # Temes de ressaltat propi (JSON de pandoc)
├── assets/                    # Recursos estàtics (logos, imatges)
├── examples/                  # Documents de prova (només les fonts .md)
├── run.sh                     # Llançador (usa el .venv local)
├── pdf.sh                     # Markdown -> PDF amb Chromium headless
├── requirements.txt           # Dependències de Python
└── pyproject.toml             # Configuració del projecte i pytest
```

> **`examples/`** conté documents de prova (`demo.md`, `Examen Linux.md`) que
> exerciten títols, llistes niuades, tasques, taules, blocs de codi i imatges.
> Les eixides `.html`/`.pdf` **no es versionen**: es generen amb l'aplicació.

## 🚀 Instal·lació

### Requisits previs

- **Python 3.10+**
- **Pandoc** instal·lat i disponible al PATH
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

La configuració de l'institut es desa a `config/institut.json`:

```json
{
  "institut_nom": "IES Pere Maria Orts i Bosch",
  "institut_logo": "assets/logoIESPereMariaOrtsiBosch.png",
  "curs": "1º DAM/DAW",
  "assignatura": "Sistemas Informáticos",
  "professor": "Pau Palacios Server",
  "departament": "Informàtica",
  "css_name": "prova.css",
  "template_name": "base.html",
  "js_name": "script.js",
  "highlight_style": "themes/one-dark.theme"
}
```

`highlight_style` pot ser un tema propi (`themes/one-dark.theme`,
`themes/material-ocean.theme`, `themes/github-dark.theme`) o el nom d'un tema
fosc de Pandoc (`zenburn`, `espresso`, `breezedark`, `monochrome`).

Pots modificar aquests valors des de la interfície (botó **⚙️ Ajustos**) o editant el fitxer directament.
