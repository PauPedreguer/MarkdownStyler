import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.ui.app import App

if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    
    style_path = Path("src/ui/style.qss")
    if style_path.exists():
        with open(style_path, "r") as f:
            app_qt.setStyleSheet(f.read())
            
    app_qt.setStyle("Fusion")
    window = App()
    window.show()
    sys.exit(app_qt.exec())
    