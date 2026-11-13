from pathlib import Path
import threading

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon

from src.core.curs import calcular_curs_academic
from src.core.identitats import (
    etiqueta_identitat,
    identitat_efectiva,
    identitat_inicial,
    nom_del_color,
)
from src.core.models import ExportOptions
from src.infrastructure.config_repo import load_institut_config
from src.infrastructure.project_paths import (
    from_project_root,
    icona_configuracio,
)
from src.use_cases.generate_html import execute_export
from src.ui.components import DropZone, SettingsDialog, SuccessDialog, PrimaryButton
from src.version import NOM

# Tira de colors de la finestra: tots en una sola fila, amb scroll horitzontal
# si no hi caben. La mostra és rodona i porta l'etiqueta davall.
MIDA_MOSTRA_COLOR = 32
AMPLADA_ETIQUETA_COLOR = 76
ALTURA_ETIQUETA_COLOR = 28
ALTURA_TIRA_COLORS = 74


class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle(NOM)
        self.setMinimumSize(480, 640)
        self.resize(620, 760)

        # Els colors d'identitat (color + curs + assignatura) ixen de la
        # configuració: des d'ací no s'editen, només es trien.
        self.config = load_institut_config()

        icona = QIcon(str(from_project_root("assets", "markdown-styler.svg")))
        if icona.isNull():
            # Sense icona pròpia, almenys la de configuració (un engranatge).
            icona = QIcon(str(icona_configuracio()))
        if not icona.isNull():
            self.setWindowIcon(icona)
        # La variant blanca és la que es veu damunt del botó blau.
        self.icona_configuracio = QIcon(str(icona_configuracio(blanca=True)))

        # --- Contenidor Scrollable ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setCentralWidget(self.scroll)

        self.container = QWidget()
        self.container.setObjectName("contenidor_principal")
        self.scroll.setWidget(self.container)

        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(24, 24, 24, 24)

        # Capçalera Premium
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 6)

        main_title = QLabel("Markdown Styler")
        main_title.setWordWrap(True)
        main_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #111827;")

        sub_title = QLabel("Editor de Pràctiques Digitals")
        sub_title.setWordWrap(True)
        sub_title.setStyleSheet("font-size: 14px; color: #6b7280; font-weight: normal;")

        header_layout.addWidget(main_title)
        header_layout.addWidget(sub_title)
        self.layout.addWidget(header_widget)

        # Colors d'identitat: cada color porta el curs i l'assignatura que té
        # assignats a Configuració. En triar-ne un, el document n'hereta el
        # color i la capçalera agafa eixe curs i eixa assignatura.
        self.identitats = self.config["identitats"]
        # El primer color de la configuració és el document per defecte.
        self.selected_color = identitat_inicial(self.identitats)["color"]
        self.color_buttons = []

        tools_layout = QHBoxLayout()
        tools_layout.addStretch()
        settings_btn = QPushButton("Configuració")
        settings_btn.setProperty("class", "secondary")
        if not self.icona_configuracio.isNull():
            settings_btn.setIcon(self.icona_configuracio)
        settings_btn.setToolTip(
            "Institut, colors d'identitat, estil i plantilla dels documents"
        )
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

        self.layout.addWidget(QLabel("Subtítol (opcional):"))
        self.subtitle_input = QLineEdit()
        self.layout.addWidget(self.subtitle_input)

        self.layout.addWidget(QLabel("Curs acadèmic:"))
        self.curs_input = QLineEdit(calcular_curs_academic())
        self.layout.addWidget(self.curs_input)

        # Un color per cada identitat (color + curs + assignatura) de la
        # configuració. Van tots en una sola fila: si no hi caben, la tira
        # s'arrissa amb la barra horitzontal.
        self.layout.addWidget(QLabel("Color, curs i assignatura del document:"))
        self.colors_strip = self._crea_tira_colors()
        self.layout.addWidget(self.colors_strip)
        self._ompli_tira_colors()
        self.layout.addStretch()

        # Botó d'exportació
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.export_btn = PrimaryButton("Generar document HTML")
        self.export_btn.clicked.connect(lambda: self.export())
        buttons_layout.addWidget(self.export_btn)

        self.layout.addLayout(buttons_layout)

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

    def _crea_tira_colors(self) -> QScrollArea:
        """Crea la tira horitzontal on van tots els colors en una sola fila.

        Returns:
            Un QScrollArea de nom ``tira_colors`` amb un QHBoxLayout dins, que
            mostra una barra horitzontal només si els colors no hi caben.
        """
        tira = QScrollArea()
        tira.setObjectName("tira_colors")
        tira.setFrameShape(QScrollArea.Shape.NoFrame)
        tira.setWidgetResizable(True)
        tira.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tira.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        tira.setFixedHeight(ALTURA_TIRA_COLORS)

        contingut = QWidget()
        self.colors_layout = QHBoxLayout(contingut)
        self.colors_layout.setContentsMargins(0, 0, 0, 0)
        self.colors_layout.setSpacing(10)
        tira.setWidget(contingut)
        return tira

    def _ompli_tira_colors(self):
        """Buida la tira i hi torna a posar un selector per cada identitat."""
        while self.colors_layout.count():
            element = self.colors_layout.takeAt(0)
            widget = element.widget()
            if widget is not None:
                widget.deleteLater()

        self.color_buttons = []
        for identitat in self.identitats:
            self.colors_layout.addWidget(
                self._crea_selector_color(identitat),
                alignment=Qt.AlignmentFlag.AlignTop,
            )
        # Sense este estiró, els colors quedarien centrats a la tira.
        self.colors_layout.addStretch(1)

    def _crea_selector_color(self, identitat):
        """Crea el bloc d'un color: el cercle i l'etiqueta de davall.

        Args:
            identitat: Diccionari amb ``color``, ``curs`` i ``assignatura``.

        Returns:
            El QWidget que s'afig a la tira de colors.
        """
        color = identitat["color"]
        etiqueta = etiqueta_identitat(identitat)

        bloc = QWidget()
        bloc_layout = QVBoxLayout(bloc)
        bloc_layout.setContentsMargins(0, 0, 0, 0)
        bloc_layout.setSpacing(4)

        boto = QPushButton()
        boto.setFixedSize(MIDA_MOSTRA_COLOR, MIDA_MOSTRA_COLOR)
        boto.setCursor(Qt.CursorShape.PointingHandCursor)
        boto.setProperty("hex", color)
        boto.setToolTip(f"{nom_del_color(color)} ({color})\n{etiqueta}")
        boto.clicked.connect(lambda checked, c=color: self.select_color(c))

        text = QLabel(etiqueta)
        text.setProperty("class", "swatch-label")
        text.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        text.setWordWrap(True)
        text.setFixedSize(AMPLADA_ETIQUETA_COLOR, ALTURA_ETIQUETA_COLOR)
        text.setToolTip(etiqueta)

        bloc_layout.addWidget(boto, alignment=Qt.AlignmentFlag.AlignHCenter)
        bloc_layout.addWidget(text)

        self.color_buttons.append(boto)
        self._pinta_selector(boto)
        return bloc

    def _pinta_selector(self, boto):
        """Dibuixa el cercle del color, amb vora gruixuda si és el triat.

        Args:
            boto: Botó del color que s'ha de repintar.
        """
        color = boto.property("hex")
        vora = "3px solid #111827" if color == self.selected_color else "none"
        boto.setStyleSheet(
            "background-color: "
            f"{color}; border-radius: {MIDA_MOSTRA_COLOR // 2}px; border: {vora};"
        )

    def select_color(self, hex_color):
        """Marca el color com a triat; el document n'hereta la identitat.

        Args:
            hex_color: Color hexadecimal del botó premut.
        """
        self.selected_color = hex_color
        for boto in self.color_buttons:
            self._pinta_selector(boto)

    def open_settings(self):
        """Obri la configuració i refresca els colors si s'ha desat.

        Els colors d'identitat es poden canviar a la configuració, així que en
        tancar el diàleg cal tornar a llegir-los i reconstruir la tira.
        """
        dialog = SettingsDialog(self)
        if not dialog.exec():
            return
        self._recarrega_identitats()

    def _recarrega_identitats(self):
        """Rellig la configuració i reconstrueix la tira de colors."""
        self.config = load_institut_config()
        self.identitats = self.config["identitats"]
        self.selected_color = identitat_inicial(self.identitats)["color"]
        self._ompli_tira_colors()

    def export(self):
        """Demana la carpeta de destí i genera el document HTML."""
        if not self.md_path_input.text():
            QMessageBox.critical(self, "Error", "Selecciona un markdown abans d'exportar.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta d'exportació")
        if not output_dir:
            return

        # Els widgets de Qt només es poden llegir al fil principal: construïm
        # ací les opcions i el fil de treball només executa l'exportació.
        # El curs i l'assignatura ixen del color d'identitat triat (o, si no en
        # porta, del document per defecte).
        identitat = identitat_efectiva(self.identitats, self.selected_color)
        options = ExportOptions(
            md_path=self.md_path_input.text(),
            output_dir=output_dir,
            title=self.title_input.text(),
            subtitol=self.subtitle_input.text(),
            curs_academic=self.curs_input.text(),
            primary_color=self.selected_color,
            curs=identitat["curs"],
            assignatura=identitat["assignatura"],
        )

        self.export_btn.setEnabled(False)
        self.export_btn.setText("Generant document... ✨")

        threading.Thread(target=self._export_thread, args=(options,), daemon=True).start()

    def _export_thread(self, options):
        """Executa l'exportació fora del fil principal.

        Només treballa amb ``options`` (construïdes al fil principal) i es
        comunica amb la interfície per senyals: llegir widgets de Qt des d'un
        fil de treball no és segur.
        """
        try:
            self.signals.finished.emit(execute_export(options))
        except Exception as e:
            self.signals.error.emit(str(e))

    def _reset_export_buttons(self):
        """Restaura el botó d'exportació al seu estat inicial."""
        self.export_btn.setEnabled(True)
        self.export_btn.setText("Generar document HTML")

    def on_export_success(self, output):
        self._reset_export_buttons()

        dialog = SuccessDialog(output, self)
        dialog.exec()

    def on_export_error(self, error_msg):
        self._reset_export_buttons()
        # Text pla: el missatge de pandoc pot contenir `<...>` i, en mode
        # enriquit, QMessageBox el prendria per HTML i es veuria tallat.
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.setText(f"Error al convertir:\n{error_msg}")
        box.exec()
