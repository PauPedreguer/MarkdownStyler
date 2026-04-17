import sys
import shutil
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
        
        self.layout.addWidget(QLabel("Estil CSS:"))
        style_layout = QHBoxLayout()
        self.style_combo = QComboBox()
        self.load_styles()
        self.add_style_btn = QPushButton("+")
        self.add_style_btn.setFixedSize(36, 40)
        self.add_style_btn.setProperty("class", "secondary")
        self.add_style_btn.setToolTip("Afegeix un nou estil .css")
        self.add_style_btn.clicked.connect(self.import_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addWidget(self.add_style_btn)
        self.layout.addLayout(style_layout)
        
        self.layout.addWidget(QLabel("Plantilla HTML:"))
        template_layout = QHBoxLayout()
        self.template_combo = QComboBox()
        self.load_templates()
        self.add_template_btn = QPushButton("+")
        self.add_template_btn.setFixedSize(36, 40)
        self.add_template_btn.setProperty("class", "secondary")
        self.add_template_btn.setToolTip("Afegeix una nova plantilla .html")
        self.add_template_btn.clicked.connect(self.import_template)
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(self.add_template_btn)
        self.layout.addLayout(template_layout)

        self.layout.addWidget(QLabel("Script JS:"))
        script_layout = QHBoxLayout()
        self.script_combo = QComboBox()
        self.load_scripts()
        self.add_script_btn = QPushButton("+")
        self.add_script_btn.setFixedSize(36, 40)
        self.add_script_btn.setProperty("class", "secondary")
        self.add_script_btn.setToolTip("Afegeix un nou script .js")
        self.add_script_btn.clicked.connect(self.import_script)
        script_layout.addWidget(self.script_combo)
        script_layout.addWidget(self.add_script_btn)
        self.layout.addLayout(script_layout)
        
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
        if not file:
            return
            
        dest_dir = Path(target_dir)
        dest_dir.mkdir(exist_ok=True)
        dest_path = dest_dir / Path(file).name
        
        if dest_path.exists():
            reply = QMessageBox.question(self, "Substituir", f"El fitxer '{dest_path.name}' ja existeix. Vols substituir-lo?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            shutil.copy(file, dest_path)
            refresh_callback()
            # Seleccionar automàticament el nou recurs
            index = combo.findText(dest_path.name)
            if index >= 0:
                combo.setCurrentIndex(index)
            QMessageBox.information(self, "Èxit", f"{resource_name} importat correctament.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No s'ha pogut importar el recurs: {str(e)}")

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
            md = self.md_path_input.text()
            base = Path(md).stem
            output = str(Path(output_dir) / f"{base}.html")
            
            css_path = ""
            if self.style_combo.currentText():
                css_path = f"styles/{self.style_combo.currentText()}"

            template_path = "templates/base.html" # Default
            if self.template_combo.currentText():
                template_path = f"templates/{self.template_combo.currentText()}"

            js_path = "" # Opcional
            if self.script_combo.currentText():
                js_path = f"scripts/{self.script_combo.currentText()}"

            options = ExportOptions(
                md_path=md,
                output_path=output,
                css_path=css_path,
                template_path=template_path,
                js_path=js_path,
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
