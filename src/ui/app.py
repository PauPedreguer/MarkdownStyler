import os
import sys
from pathlib import Path
from datetime import datetime
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox,
    QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from src.core.models import ExportOptions
from src.use_cases.generate_html import execute_export
from src.infrastructure.config_repo import load_institut_config, save_institut_config

class DropZone(QWidget):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("drop_zone_widget")
        self.setMinimumHeight(120)
        self.setStyleSheet("""
            QWidget#drop_zone_widget {
                border: 2px dashed #93c5fd;
                border-radius: 12px;
                background: #eff6ff;
            }
            QLabel {
                font-size: 15px;
                color: #2563eb;
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)
        layout = QVBoxLayout(self)
        self.label = QLabel("📥 Arrossega aquí el teu fitxer .md")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasUrls():
            return
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not file_path and hasattr(url, "path"):
                file_path = url.path()
            if file_path.endswith('.md'):
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
                return

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
        self.logo_btn.setStyleSheet("padding: 8px; font-weight: bold;")
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
        
        save_btn = QPushButton("Desar Ajustos")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981; 
                color: white; 
                font-weight: bold; 
                padding: 10px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
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

class SuccessDialog(QDialog):
    def __init__(self, output_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportació Finalitzada")
        self.setMinimumWidth(400)
        self.output_path = output_path
        
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel.title { font-size: 18px; font-weight: bold; color: #10b981; }
            QLabel.subtitle { font-size: 13px; color: #374151; }
            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                border: none;
            }
            QPushButton#btn_ok {
                background-color: #f3f4f6;
                color: #374151;
            }
            QPushButton#btn_ok:hover { background-color: #e5e7eb; }
            QPushButton#btn_open {
                background-color: #2563eb;
                color: white;
            }
            QPushButton#btn_open:hover { background-color: #1d4ed8; }
        """)
        
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
        btn_ok.setObjectName("btn_ok")
        btn_ok.clicked.connect(self.accept)
        
        btn_open = QPushButton("Obrir Fitxer")
        btn_open.setObjectName("btn_open")
        btn_open.clicked.connect(self.open_file)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_open)
        
        layout.addLayout(btn_layout)
        
    def open_file(self):
        import webbrowser
        webbrowser.open(f"file://{self.output_path}")
        self.accept()

class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("Markdown Styler Premium")
        self.setMinimumSize(550, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QWidget { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
            QLabel { font-weight: 600; color: #374151; font-size: 14px; }
            QLineEdit, QComboBox { 
                padding: 12px; 
                border: 1px solid #d1d5db; 
                border-radius: 6px; 
                background: #f9fafb; 
                color: #111827; 
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #2563eb; background: #ffffff; }
        """)
        
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.layout = QVBoxLayout(self.centralwidget)
        self.layout.setSpacing(18)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        tools_layout = QHBoxLayout()
        tools_layout.addStretch()
        settings_btn = QPushButton("⚙️ Ajustos")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        settings_btn.clicked.connect(self.open_settings)
        tools_layout.addWidget(settings_btn)
        self.layout.addLayout(tools_layout)
        
        self.layout.addWidget(QLabel("Fitxer Markdown o Directori:"))
        md_layout = QHBoxLayout()
        self.md_path_input = QLineEdit()
        self.md_btn = QPushButton("Seleccionar")
        self.md_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.md_btn.clicked.connect(self.select_md)
        md_layout.addWidget(self.md_path_input)
        md_layout.addWidget(self.md_btn)
        self.layout.addLayout(md_layout)
        
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.handle_drop)
        self.layout.addWidget(self.drop_zone)
        
        self.layout.addWidget(QLabel("Estil CSS:"))
        self.style_combo = QComboBox()
        self.load_styles()
        self.layout.addWidget(self.style_combo)
        
        self.layout.addWidget(QLabel("Títol de la pràctica:"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)
        
        self.layout.addWidget(QLabel("Data:"))
        self.data_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.layout.addWidget(self.data_input)
        
        self.layout.addStretch()
        
        self.export_btn = QPushButton("Exportar HTML")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 14px;
                font-size: 15px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #93c5fd; }
        """)
        self.export_btn.clicked.connect(self.export)
        self.layout.addWidget(self.export_btn)
        
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.on_export_success)
        self.signals.error.connect(self.on_export_error)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasUrls():
            return
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not file_path and hasattr(url, "path"):
                file_path = url.path()
            if file_path.endswith('.md'):
                self.md_path_input.setText(file_path)
                if not self.title_input.text():
                    self.title_input.setText(Path(file_path).stem)
                event.acceptProposedAction()
                return

    def load_styles(self):
        styles_dir = Path("styles")
        if styles_dir.exists():
            for f in sorted(styles_dir.glob("*.css")):
                self.style_combo.addItem(f.name)

    def select_md(self):
        file, _ = QFileDialog.getOpenFileName(self, "Obrir Markdown", "", "Markdown (*.md)")
        if file:
            self.handle_drop(file)
            
    def handle_drop(self, file_path):
        self.md_path_input.setText(file_path)
        if not self.title_input.text():
            self.title_input.setText(Path(file_path).stem)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def export(self):
        if not self.md_path_input.text():
            QMessageBox.critical(self, "Error", "Selecciona un markdown abans d'exportar.")
            return
            
        output_dir = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta d'exportació")
        if not output_dir:
            return
            
        self.export_btn.setEnabled(False)
        self.export_btn.setText("Exportant atèntament...")
        
        threading.Thread(target=self._export_thread, args=(output_dir,), daemon=True).start()

    def _export_thread(self, output_dir):
        md = self.md_path_input.text()
        base = Path(md).stem
        output = os.path.join(output_dir, f"{base}.html")
        
        css_path = ""
        if self.style_combo.currentText():
            css_path = f"styles/{self.style_combo.currentText()}"

        try:
            options = ExportOptions(
                md_path=md,
                output_path=output,
                css_path=css_path,
                title=self.title_input.text(),
                data=self.data_input.text()
            )
            execute_export(options)
            self.signals.finished.emit(output)
        except Exception as e:
            self.signals.error.emit(str(e))
            
    def on_export_success(self, output):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("Exportar HTML")

        dialog = SuccessDialog(output, self)
        dialog.exec()
        
    def on_export_error(self, error_msg):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("Exportar HTML")
        QMessageBox.critical(self, "Error", f"Error al convertir:\n{error_msg}")
