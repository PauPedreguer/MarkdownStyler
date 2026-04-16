import sys
from PyQt6.QtWidgets import QApplication
from src.ui.app import App

if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    app_qt.setStyle("Fusion")
    window = App()
    window.show()
    sys.exit(app_qt.exec())