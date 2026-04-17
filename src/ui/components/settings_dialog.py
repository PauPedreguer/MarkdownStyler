from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox
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
        
        save_btn = PrimaryButton("Desar Ajustos")
        save_btn.clicked.connect(self.save_config)
        layout.addRow(save_btn)
        
    def browse_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imatges (*.png *.jpg *.jpeg *.svg)")
        if file:
            self.logo_input.setText(file)
            
    def save_config(self):
        new_config = {
            "institut_nom": self.nom_input.text(),
            "institut_logo": self.logo_input.text(),
            "curs": self.curs_input.text(),
            "assignatura": self.assig_input.text(),
            "professor": self.prof_input.text()
        }
        save_institut_config(new_config)
        QMessageBox.information(self, "Guardat", "S'han desat els ajustos de manera persistent.")
        self.accept()
