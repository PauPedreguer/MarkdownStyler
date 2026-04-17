from PyQt6.QtWidgets import QPushButton

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "primary")
