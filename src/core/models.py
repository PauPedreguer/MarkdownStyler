from dataclasses import dataclass

from src.core.identitats import COLOR_PER_DEFECTE

@dataclass
class ExportOptions:
    """Opcions d'exportació a HTML.

    El PDF no es genera a l'aplicació: s'obté imprimint l'HTML des del
    navegador (botó 🖨️ del document o ``pdf.sh``).
    """

    md_path: str
    output_dir: str
    title: str
    curs_academic: str
    subtitol: str = ""
    # Buit → s'usa el departament de config/institut.json, que és on l'usuari
    # el configura (el formulari principal no el demana).
    departament: str = ""
    primary_color: str = COLOR_PER_DEFECTE
    # Curs (el grup: "1r DAW") i assignatura del document. Els ompli la finestra
    # a partir del color d'identitat triat; buits → s'usen els de
    # config/institut.json. No confondre ``curs`` (el grup) amb
    # ``curs_academic`` (l'any: "26-27").
    curs: str = ""
    assignatura: str = ""

