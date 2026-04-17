import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from src.ui.components.buttons import PrimaryButton

class SuccessDialog(QDialog):
    def __init__(self, output_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportació Finalitzada")
        self.setMinimumWidth(400)
        self.output_path = output_path
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        title = QLabel("L'HTML s'ha generat correctament 🎉")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(f"S'ha desat a: {output_path}")
        subtitle.setProperty("class", "subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(15)
        
        btn_ok = QPushButton("D'acord")
        btn_ok.setProperty("class", "outline")
        btn_ok.clicked.connect(self.accept)
        
        btn_open = PrimaryButton("Obrir Fitxer")
        btn_open.clicked.connect(self.open_file)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_open)
        
        layout.addLayout(btn_layout)
        
    def open_file(self):
        webbrowser.open(f"file://{self.output_path}")
        self.accept()
