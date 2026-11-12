import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox
)
from src.infrastructure.config_repo import load_institut_config, save_institut_config
from src.infrastructure.project_paths import from_project_root
from src.ui.components.buttons import PrimaryButton

# Fitxers de suport: s'utilitzen internament però no s'han d'oferir com a
# recurs seleccionable. base.css es carrega sempre abans de l'estil triat,
# pdf.css només té sentit per a l'exportació PDF i highlight.min.js és una
# llibreria de tercers, no un script de la plantilla.
CSS_NO_SELECCIONABLES = frozenset({"base.css", "pdf.css"})
JS_NO_SELECCIONABLES = frozenset({"highlight.min.js"})


def recursos_disponibles(directori: Path, extensio: str, exclusions: frozenset) -> list:
    """Retorna els recursos seleccionables d'un directori, ordenats per nom.

    Args:
        directori: Directori a explorar (pot no existir).
        extensio: Extensió a filtrar, per exemple ``".css"``.
        exclusions: Noms de fitxer que no s'han d'incloure a la llista.

    Returns:
        La llista de noms de fitxer, ordenada alfabèticament.
    """
    if not directori.exists():
        return []
    return sorted(
        fitxer.name
        for fitxer in directori.glob(f"*{extensio}")
        if fitxer.name not in exclusions
    )


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustos de l'Institut")
        self.setMinimumWidth(450)
        self.config = load_institut_config()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.nom_input = QLineEdit(self.config.get("institut_nom", ""))
        layout.addRow(QLabel("Nom de l'institut:"), self.nom_input)
        
        logo_layout = QHBoxLayout()
        self.logo_input = QLineEdit(self.config.get("institut_logo", ""))
        self.logo_btn = QPushButton("Cercar")
        self.logo_btn.setProperty("class", "secondary")
        self.logo_btn.clicked.connect(self.browse_logo)
        logo_layout.addWidget(self.logo_input)
        logo_layout.addWidget(self.logo_btn)
        layout.addRow(QLabel("Ruta del Logo:"), logo_layout)
        
        self.curs_input = QLineEdit(self.config.get("curs", ""))
        layout.addRow(QLabel("Curs:"), self.curs_input)
        
        self.assig_input = QLineEdit(self.config.get("assignatura", ""))
        layout.addRow(QLabel("Assignatura:"), self.assig_input)
        
        self.prof_input = QLineEdit(self.config.get("professor", ""))
        layout.addRow(QLabel("Professor:"), self.prof_input)
        
        self.dept_input = QLineEdit(self.config.get("departament", "Informàtica"))
        layout.addRow(QLabel("Departament:"), self.dept_input)
        
        # --- Secció Configuració de Documents ---
        header = QLabel("CONFIGURACIÓ DE DOCUMENTS")
        header.setProperty("class", "section-header")
        layout.addRow(header)
        
        # Estil CSS
        style_layout = QHBoxLayout()
        self.style_combo = QComboBox()
        self.load_styles()
        
        # Seleccionar estils actuals als combos
        idx_style = self.style_combo.findText(self.config.get("css_name", "prova.css"))
        if idx_style >= 0: self.style_combo.setCurrentIndex(idx_style)
        
        self.template_combo = QComboBox()
        self.load_templates()
        idx_temp = self.template_combo.findText(self.config.get("template_name", "base.html"))
        if idx_temp >= 0: self.template_combo.setCurrentIndex(idx_temp)
        
        self.script_combo = QComboBox()
        self.load_scripts()
        idx_script = self.script_combo.findText(self.config.get("js_name", "script.js"))
        if idx_script >= 0: self.script_combo.setCurrentIndex(idx_script)

        self.highlight_combo = QComboBox()
        self.highlight_combo.addItems(["pygments", "tango", "espresso", "zenburn", "kate", "monochrome", "breezedark", "haddock"])
        idx_h = self.highlight_combo.findText(self.config.get("highlight_style", "zenburn"))
        if idx_h >= 0: self.highlight_combo.setCurrentIndex(idx_h)
        
        self.add_style_btn = QPushButton("+")
        self.add_style_btn.setFixedSize(30, 30)
        self.add_style_btn.setProperty("class", "secondary")
        self.add_style_btn.clicked.connect(self.import_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addWidget(self.add_style_btn)
        layout.addRow(QLabel("Estil CSS:"), style_layout)
        
        # Plantilla HTML
        template_layout = QHBoxLayout()
        self.add_template_btn = QPushButton("+")
        self.add_template_btn.setFixedSize(30, 30)
        self.add_template_btn.setProperty("class", "secondary")
        self.add_template_btn.clicked.connect(self.import_template)
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(self.add_template_btn)
        layout.addRow(QLabel("Plantilla HTML:"), template_layout)
        
        # Script JS
        script_layout = QHBoxLayout()
        self.add_script_btn = QPushButton("+")
        self.add_script_btn.setFixedSize(30, 30)
        self.add_script_btn.setProperty("class", "secondary")
        self.add_script_btn.clicked.connect(self.import_script)
        script_layout.addWidget(self.script_combo)
        script_layout.addWidget(self.add_script_btn)
        layout.addRow(QLabel("Script JS:"), script_layout)
        
        layout.addRow(QLabel("<br>"))
        # Estil de Codi (Highlight)
        layout.addRow(QLabel("Ressaltat de codi:"), self.highlight_combo)
        
        save_btn = PrimaryButton("Desar Ajustos")
        save_btn.clicked.connect(self.save_config)
        layout.addRow(save_btn)
        
    def browse_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imatges (*.png *.jpg *.jpeg *.svg)")
        if file:
            self.logo_input.setText(file)

    def load_styles(self):
        self.style_combo.clear()
        self.style_combo.addItems(
            recursos_disponibles(
                from_project_root("styles"), ".css", CSS_NO_SELECCIONABLES
            )
        )

    def load_templates(self):
        self.template_combo.clear()
        self.template_combo.addItems(
            recursos_disponibles(from_project_root("templates"), ".html", frozenset())
        )

    def load_scripts(self):
        self.script_combo.clear()
        self.script_combo.addItems(
            recursos_disponibles(
                from_project_root("scripts"), ".js", JS_NO_SELECCIONABLES
            )
        )

    def import_style(self):
        self.import_resource("styles", "*.css", "Estil CSS", self.load_styles, self.style_combo)

    def import_template(self):
        self.import_resource("templates", "*.html", "Plantilla HTML", self.load_templates, self.template_combo)

    def import_script(self):
        self.import_resource("scripts", "*.js", "Script JS", self.load_scripts, self.script_combo)

    def import_resource(self, target_dir, file_filter, resource_name, refresh_callback, combo):
        file, _ = QFileDialog.getOpenFileName(self, f"Importar {resource_name}", "", f"{resource_name} ({file_filter})")
        if not file: return
            
        dest_dir = from_project_root(target_dir)
        dest_dir.mkdir(exist_ok=True)
        dest_path = dest_dir / Path(file).name
        
        if dest_path.exists():
            reply = QMessageBox.question(self, "Substituir", f"El fitxer '{dest_path.name}' ja existeix. Vols substituir-lo?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return
        
        try:
            shutil.copy(file, dest_path)
            refresh_callback()
            index = combo.findText(dest_path.name)
            if index >= 0: combo.setCurrentIndex(index)
            QMessageBox.information(self, "Èxit", f"{resource_name} importat correctament.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No s'ha pogut importar el recurs: {str(e)}")
            
    def save_config(self):
        new_config = {
            "institut_nom": self.nom_input.text(),
            "institut_logo": self.logo_input.text(),
            "curs": self.curs_input.text(),
            "assignatura": self.assig_input.text(),
            "professor": self.prof_input.text(),
            "departament": self.dept_input.text(),
            "css_name": self.style_combo.currentText(),
            "template_name": self.template_combo.currentText(),
            "js_name": self.script_combo.currentText(),
            "highlight_style": self.highlight_combo.currentText()
        }
        save_institut_config(new_config)
        QMessageBox.information(self, "Guardat", "S'han desat els ajustos de manera persistent.")
        self.accept()
