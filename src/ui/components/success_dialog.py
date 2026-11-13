import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from src.ui.components.buttons import PrimaryButton


def url_fitxer(path) -> str:
    """Converteix una ruta del sistema en una URL ``file://`` vàlida.

    ``f"file://{path}"`` no funciona amb espais ni accents (el navegador no
    troba el fitxer). ``Path.as_uri()`` els escapa correctament.

    Args:
        path: Ruta del fitxer (absoluta o relativa).

    Returns:
        La URL ``file://`` equivalent, amb els caràcters escapats.
    """
    return Path(path).resolve().as_uri()


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
        
        title = QLabel("Fitxer generat correctament 🎉")
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
        
        btn_present = QPushButton("▶ Presentar")
        btn_present.setProperty("class", "outline")
        btn_present.setToolTip(
            "Obri el document directament en mode presentació (també amb P o F5)."
        )
        btn_present.clicked.connect(self.presentar)

        btn_open = PrimaryButton("Obrir Fitxer")
        btn_open.clicked.connect(self.open_file)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_present)
        btn_layout.addWidget(btn_open)
        
        layout.addLayout(btn_layout)
        
    def open_file(self):
        webbrowser.open(url_fitxer(self.output_path))
        self.accept()

    def presentar(self):
        """Obri el document directament en mode presentació.

        El script del document llig el hash ``#presentar`` en carregar, així
        que no cal cap paràmetre més ni una pàgina a banda.
        """
        webbrowser.open(url_fitxer(self.output_path) + "#presentar")
        self.accept()
