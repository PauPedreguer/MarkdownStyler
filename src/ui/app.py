import sys
import shutil
from pathlib import Path
from datetime import datetime
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QScrollArea
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
        self.setMinimumSize(450, 600)
        
        # --- Contenidor Scrollable ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setCentralWidget(self.scroll)
        
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(18)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Capçalera Premium
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        main_title = QLabel("Markdown Styler")
        main_title.setWordWrap(True)
        main_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #111827;")
        
        sub_title = QLabel("Editor de Pràctiques Digitals")
        sub_title.setWordWrap(True)
        sub_title.setStyleSheet("font-size: 14px; color: #6b7280; font-weight: normal;")
        
        header_layout.addWidget(main_title)
        header_layout.addWidget(sub_title)
        self.layout.addWidget(header_widget)
        
        # Estat de color
        self.selected_color = "#1d4ed8" # Blau Professional per defecte
        self.color_buttons = []
        
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
        
        self.layout.addWidget(QLabel("Títol de la pràctica:"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)
        
        self.layout.addWidget(QLabel("Data:"))
        self.data_input = QLineEdit(datetime.now().strftime("%d-%m-%Y"))
        self.layout.addWidget(self.data_input)
        
        # Presets de color
        self.layout.addWidget(QLabel("Color d'identitat:"))
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(10)
        
        presets = [
            ("#1d4ed8", "Blau"),
            ("#047857", "Verd"),
            ("#b91c1c", "Vermell"),
            ("#b45309", "Taronja"),
            ("#6d28d9", "Violeta")
        ]
        
        for hex_color, name in presets:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(name)
            btn.setProperty("hex", hex_color)
            
            # Estat inicial
            border = "3px solid #111827" if hex_color == self.selected_color else "none"
            btn.setStyleSheet(f"background-color: {hex_color}; border-radius: 16px; border: {border};")
            
            btn.clicked.connect(lambda checked, c=hex_color, b=btn: self.select_color(c, b))
            colors_layout.addWidget(btn)
            self.color_buttons.append(btn)
            
        colors_layout.addStretch()
        self.layout.addLayout(colors_layout)
        
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

    def select_md(self):
        file, _ = QFileDialog.getOpenFileName(self, "Obrir Markdown", "", "Markdown (*.md)")
        if file:
            self.handle_drop(file)
            
    def handle_drop(self, file_path):
        self.md_path_input.setText(file_path)
        if not self.title_input.text():
            self.title_input.setText(Path(file_path).stem)

    def select_color(self, hex_color, button):
        self.selected_color = hex_color
        # Actualitzar estils visuals dels botons
        for btn in self.color_buttons:
            c = btn.property("hex")
            border = "3px solid #111827" if c == self.selected_color else "none"
            btn.setStyleSheet(f"background-color: {c}; border-radius: 16px; border: {border};")

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
        try:
            from src.infrastructure.config_repo import load_institut_config
            config = load_institut_config()
            
            md = self.md_path_input.text()
            base = Path(md).stem
            output = str(Path(output_dir) / f"{base}.html")
            
            css_name = config.get("css_name", "prova.css")
            css_path = f"styles/{css_name}" if css_name else "styles/prova.css"

            template_name = config.get("template_name", "base.html")
            template_path = f"templates/{template_name}" if template_name else "templates/base.html"

            js_name = config.get("js_name", "script.js")
            js_path = f"scripts/{js_name}" if js_name else "scripts/script.js"

            highlight_style = config.get("highlight_style", "zenburn")

            options = ExportOptions(
                md_path=md,
                output_path=output,
                css_path=css_path,
                template_path=template_path,
                js_path=js_path,
                highlight_style=highlight_style,
                title=self.title_input.text(),
                data=self.data_input.text(),
                primary_color=self.selected_color
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
