# Markdown Styler

Aplicació d'escriptori (PyQt6) que genera documents HTML i PDF amb estil professional a partir de fitxers Markdown, utilitzant **Pandoc** com a motor de conversió.

## ✨ Característiques

- 🎨 **Personalització de colors**: presets de color d'identitat configurables.
- 📄 **Documents HTML i PDF**: genera l'HTML amb portada, sumari i estil professional; el PDF s'obté imprimint-lo des del navegador (botó 🖨️ del document o `./pdf.sh`).
- 🏫 **Configuració de l'institut**: nom, logo, curs, assignatura, professor i departament.
- 🎯 **Ressaltat de codi**: el genera Pandoc (`--highlight-style`), amb estils com Zenburn, Pygments, Tango o Breeze Dark. Sense llibreries externes.
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
│   ├── test_templates.py      # Invariants de plantilla/JS de l'HTML generat
│   ├── test_pdf_script.py     # PDF de punta a punta (es salta sense Chromium)
│   └── test_ui.py             # Helpers d'UI (sense QApplication)
├── config/                    # Configuració de l'institut (JSON)
├── templates/                 # Plantilles HTML de Pandoc
├── styles/                    # Fulls d'estil CSS
├── scripts/                   # Scripts JS per als documents generats
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
  "highlight_style": "zenburn"
}
```

Pots modificar aquests valors des de la interfície (botó **⚙️ Ajustos**) o editant el fitxer directament.
