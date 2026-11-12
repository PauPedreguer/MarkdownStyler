import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.app import App
from src.infrastructure.project_paths import from_project_root


def aplica_tema(app_qt) -> None:
    """Aplica a l'aplicació l'estil Fusion i el full QSS de la interfície.

    L'ordre importa: ``setStyle()`` reconstrueix el motor d'estil i descarta
    part dels retocs que ha aplicat el ``setStyleSheet()``, de manera que
    primer s'ha de fixar l'estil (Fusion, consistent a totes les plataformes)
    i després carregar el QSS. El QSS es llig sempre en UTF-8 perquè no depén
    del locale del sistema (amb un locale no UTF-8 fallaria o es veuria mal).

    Args:
        app_qt: Instància de ``QApplication``.
    """
    app_qt.setStyle("Fusion")

    style_path = from_project_root("src", "ui", "style.qss")
    if style_path.exists():
        app_qt.setStyleSheet(style_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    # Suport per a pantalles de alta resolució (Retina/4K)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app_qt = QApplication(sys.argv)
    
    aplica_tema(app_qt)

    window = App()
    window.show()
    sys.exit(app_qt.exec())
    

    