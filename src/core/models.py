from dataclasses import dataclass

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
    primary_color: str = "#1d4ed8"
