import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.app import App
from src.infrastructure.project_paths import from_project_root

if __name__ == "__main__":
    # Suport per a pantalles de alta resolució (Retina/4K)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app_qt = QApplication(sys.argv)
    
    style_path = from_project_root("src", "ui", "style.qss")
    if style_path.exists():
        with open(style_path, "r") as f:
            app_qt.setStyleSheet(f.read())
            
    app_qt.setStyle("Fusion")
    window = App()
    window.show()
    sys.exit(app_qt.exec())
    

    