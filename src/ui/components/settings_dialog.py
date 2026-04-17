import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox
)
from src.infrastructure.config_repo import load_institut_config, save_institut_config
from src.ui.components.buttons import PrimaryButton

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
        
        # --- Secció Configuració de Documents ---
        header = QLabel("CONFIGURACIÓ DE DOCUMENTS")
        header.setProperty("class", "section-header")
        layout.addRow(header)
        
        # Estil CSS
        style_layout = QHBoxLayout()
        self.style_combo = QComboBox()
        self.load_styles()
        # Seleccionar valor guardat
        idx = self.style_combo.findText(self.config.get("css_name", ""))
        if idx >= 0: self.style_combo.setCurrentIndex(idx)
        
        self.add_style_btn = QPushButton("+")
        self.add_style_btn.setFixedSize(30, 30)
        self.add_style_btn.setProperty("class", "secondary")
        self.add_style_btn.clicked.connect(self.import_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addWidget(self.add_style_btn)
        layout.addRow(QLabel("Estil CSS:"), style_layout)
        
        # Plantilla HTML
        template_layout = QHBoxLayout()
        self.template_combo = QComboBox()
        self.load_templates()
        idx = self.template_combo.findText(self.config.get("template_name", ""))
        if idx >= 0: self.template_combo.setCurrentIndex(idx)
        
        self.add_template_btn = QPushButton("+")
        self.add_template_btn.setFixedSize(30, 30)
        self.add_template_btn.setProperty("class", "secondary")
        self.add_template_btn.clicked.connect(self.import_template)
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(self.add_template_btn)
        layout.addRow(QLabel("Plantilla HTML:"), template_layout)
        
        # Script JS
        script_layout = QHBoxLayout()
        self.script_combo = QComboBox()
        self.load_scripts()
        idx = self.script_combo.findText(self.config.get("js_name", ""))
        if idx >= 0: self.script_combo.setCurrentIndex(idx)
        
        self.add_script_btn = QPushButton("+")
        self.add_script_btn.setFixedSize(30, 30)
        self.add_script_btn.setProperty("class", "secondary")
        self.add_script_btn.clicked.connect(self.import_script)
        script_layout.addWidget(self.script_combo)
        script_layout.addWidget(self.add_script_btn)
        layout.addRow(QLabel("Script JS:"), script_layout)
        
        layout.addRow(QLabel("<br>"))
        
        save_btn = PrimaryButton("Desar Ajustos")
        save_btn.clicked.connect(self.save_config)
        layout.addRow(save_btn)
        
    def browse_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imatges (*.png *.jpg *.jpeg *.svg)")
        if file:
            self.logo_input.setText(file)

    def load_styles(self):
        self.style_combo.clear()
        styles_dir = Path("styles")
        if styles_dir.exists():
            for f in sorted(styles_dir.glob("*.css")):
                self.style_combo.addItem(f.name)

    def load_templates(self):
        self.template_combo.clear()
        templates_dir = Path("templates")
        if templates_dir.exists():
            for f in sorted(templates_dir.glob("*.html")):
                self.template_combo.addItem(f.name)

    def load_scripts(self):
        self.script_combo.clear()
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            for f in sorted(scripts_dir.glob("*.js")):
                self.script_combo.addItem(f.name)

    def import_style(self):
        self.import_resource("styles", "*.css", "Estil CSS", self.load_styles, self.style_combo)

    def import_template(self):
        self.import_resource("templates", "*.html", "Plantilla HTML", self.load_templates, self.template_combo)

    def import_script(self):
        self.import_resource("scripts", "*.js", "Script JS", self.load_scripts, self.script_combo)

    def import_resource(self, target_dir, file_filter, resource_name, refresh_callback, combo):
        file, _ = QFileDialog.getOpenFileName(self, f"Importar {resource_name}", "", f"{resource_name} ({file_filter})")
        if not file: return
            
        dest_dir = Path(target_dir)
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
            "css_name": self.style_combo.currentText(),
            "template_name": self.template_combo.currentText(),
            "js_name": self.script_combo.currentText()
        }
        save_institut_config(new_config)
        QMessageBox.information(self, "Guardat", "S'han desat els ajustos de manera persistent.")
        self.accept()
