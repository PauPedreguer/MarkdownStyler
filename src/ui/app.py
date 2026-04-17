import os
import sys
from pathlib import Path
from datetime import datetime
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from src.core.models import ExportOptions
from src.use_cases.generate_html import execute_export
from src.ui.components import DropZone, SettingsDialog, SuccessDialog, PrimaryButton

class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("Markdown Styler Premium")
        self.setMinimumSize(550, 700)
        
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.layout = QVBoxLayout(self.centralwidget)
        self.layout.setSpacing(18)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        tools_layout = QHBoxLayout()
        tools_layout.addStretch()
        settings_btn = QPushButton("⚙️ Ajustos")
        settings_btn.setProperty("class", "secondary")
        settings_btn.clicked.connect(self.open_settings)
        tools_layout.addWidget(settings_btn)
        self.layout.addLayout(tools_layout)
        
        self.layout.addWidget(QLabel("Fitxer Markdown o Directori:"))
        md_layout = QHBoxLayout()
        self.md_path_input = QLineEdit()
        self.md_btn = QPushButton("Seleccionar")
        self.md_btn.setProperty("class", "secondary")
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
        
        self.export_btn = PrimaryButton("Exportar HTML")
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
