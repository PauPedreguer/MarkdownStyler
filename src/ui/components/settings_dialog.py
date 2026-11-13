import shutil
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView, QColorDialog, QComboBox, QDialog, QFileDialog,
    QFormLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QTableWidget, QVBoxLayout, QWidget,
)
from src.core.identitats import (
    color_per_nom,
    nom_curt_del_color,
    normalitza_identitats,
    presets_per_defecte,
)
from src.infrastructure.config_repo import load_institut_config, save_institut_config
from src.infrastructure.highlight_styles import (
    ESTIL_RESSALTAT_DEFECTE,
    ESTILS_RESSALTAT,
)
from src.infrastructure.project_paths import (
    directoris_de_recurs,
    from_data_root,
    icona_configuracio,
)
from src.ui.components.buttons import PrimaryButton

# Fitxers de suport: s'utilitzen internament però no s'han d'oferir com a
# recurs seleccionable. base.css es carrega sempre abans de l'estil triat i
# presentacio.css després; cap dels dos no és un estil triable.
CSS_NO_SELECCIONABLES = frozenset({"base.css", "presentacio.css"})
JS_NO_SELECCIONABLES = frozenset({"highlight.min.js", "presentacio.js"})


def recursos_disponibles(directori, extensio: str, exclusions: frozenset) -> list:
    """Retorna els recursos seleccionables d'un directori, ordenats per nom.

    Args:
        directori: Directori a explorar (pot no existir) o una tupla de
            directoris, per exemple els de :func:`directoris_de_recurs`
            (primer el de l'usuari i després el del paquet).
        extensio: Extensió a filtrar, per exemple ``".css"``.
        exclusions: Noms de fitxer que no s'han d'incloure a la llista.

    Returns:
        La llista de noms de fitxer, sense repetits i ordenada alfabèticament.
    """
    directoris = directori if isinstance(directori, (tuple, list)) else (directori,)
    noms = set()
    for directori_actual in directoris:
        if not directori_actual.exists():
            continue
        noms.update(
            fitxer.name
            for fitxer in directori_actual.glob(f"*{extensio}")
            if fitxer.name not in exclusions
        )
    return sorted(noms)


# Columnes de la taula de colors d'identitat (Configuració).
COLUMNES_COLORS_TAULA = ("Color", "Curs", "Assignatura")
# Alçada de cada fila: hi ha de cabre el camp de text i la mostra del color.
ALCADA_FILA_COLORS = 34
# La taula creix amb les files fins a este màxim; a partir d'ací ja s'arrissa.
MAX_FILES_TAULA_VISIBLES = 6
# Mides del diàleg: el contingut va dins d'un QScrollArea perquè no cresca més
# que la pantalla on s'obri.
MIDA_INICIAL_DIALEG = (620, 760)
ALTURA_MAXIMA_DIALEG = 860


class SettingsDialog(QDialog):
    """Configuració de l'institut, dels colors d'identitat i dels documents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuració")
        self.setMinimumWidth(560)
        icona = QIcon(str(icona_configuracio()))
        if not icona.isNull():
            self.setWindowIcon(icona)
        self.config = load_institut_config()
        self.identitats = normalitza_identitats(self.config.get("identitats"))
        self.setup_ui()

    def setup_ui(self):
        """Munta el diàleg: institut, colors d'identitat i documents."""
        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(0, 0, 0, 0)
        exterior.setSpacing(0)

        # El formulari va dins d'un scroll perquè el diàleg no cresca més que la
        # pantalla; el botó de guardar queda fora, sempre a la vista.
        self.scroll = QScrollArea()
        self.scroll.setObjectName("scroll_configuracio")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        contingut = QWidget()
        contingut.setObjectName("contenidor_configuracio")
        layout = QFormLayout(contingut)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self._seccio_institut(layout)
        self._seccio_colors(layout)
        self._seccio_documents(layout)

        self.scroll.setWidget(contingut)
        exterior.addWidget(self.scroll, 1)

        peu_widget = QWidget()
        peu_widget.setObjectName("peu_configuracio")
        peu = QHBoxLayout(peu_widget)
        peu.setContentsMargins(24, 12, 24, 20)
        save_btn = PrimaryButton("Desar configuració")
        save_btn.clicked.connect(self.save_config)
        peu.addWidget(save_btn)
        exterior.addWidget(peu_widget)

        self._ajusta_mida()

    @staticmethod
    def _etiqueta_seccio(text: str) -> QLabel:
        """Retorna el títol d'una secció del formulari.

        Args:
            text: Text del títol (en majúscules).

        Returns:
            El QLabel amb l'estil de capçalera de secció.
        """
        etiqueta = QLabel(text)
        etiqueta.setProperty("class", "section-header")
        return etiqueta

    @staticmethod
    def _amb_boto(camp: QWidget, boto: QPushButton) -> QHBoxLayout:
        """Posa un camp i un botó a la mateixa fila.

        Args:
            camp: Camp que s'emporta l'espai disponible (QLineEdit, QComboBox).
            boto: Botó d'acció que acompanya el camp.

        Returns:
            El QHBoxLayout amb el camp i el botó.
        """
        fila = QHBoxLayout()
        fila.addWidget(camp)
        fila.addWidget(boto)
        return fila

    def _ajusta_mida(self) -> None:
        """Deixa el diàleg dins de la pantalla on s'obri."""
        ample, alt = MIDA_INICIAL_DIALEG
        pantalla = self.screen()
        if pantalla is not None:
            visible = pantalla.availableGeometry()
            ample = min(ample, max(visible.width() - 40, 400))
            alt = min(alt, max(visible.height() - 40, 400), ALTURA_MAXIMA_DIALEG)
        self.resize(ample, alt)

    def _seccio_institut(self, layout: QFormLayout) -> None:
        """Afig les dades de l'institut i del professorat.

        Args:
            layout: Formulari on s'afegeixen les files.
        """
        layout.addRow(self._etiqueta_seccio("INSTITUT"))

        self.nom_input = QLineEdit(self.config.get("institut_nom", ""))
        layout.addRow(QLabel("Nom de l'institut:"), self.nom_input)

        self.logo_input = QLineEdit(self.config.get("institut_logo", ""))
        self.logo_btn = QPushButton("Cercar")
        self.logo_btn.setProperty("class", "secondary")
        self.logo_btn.clicked.connect(self.browse_logo)
        layout.addRow(
            QLabel("Ruta del Logo:"), self._amb_boto(self.logo_input, self.logo_btn)
        )

        self.prof_input = QLineEdit(self.config.get("professor", ""))
        layout.addRow(QLabel("Professor:"), self.prof_input)

        self.dept_input = QLineEdit(self.config.get("departament", "Informàtica"))
        layout.addRow(QLabel("Departament:"), self.dept_input)

    def _seccio_colors(self, layout: QFormLayout) -> None:
        """Afig la taula de colors d'identitat i els botons que la gestionen.

        Args:
            layout: Formulari on s'afegeixen les files.
        """
        # Cada color porta el seu curs i la seua assignatura: la taula és
        # l'única font d'estes dades (ja no hi ha curs/assignatura per defecte).
        layout.addRow(self._etiqueta_seccio("COLORS D'IDENTITAT"))

        self._files: list[dict] = []
        self._refresc = False
        self.colors_table = self._crea_taula_colors()
        self._ompli_taula(self.identitats or presets_per_defecte())
        layout.addRow(self.colors_table)

        colors_btns = QHBoxLayout()
        for text, consell, estil, accio in (
            ("Afegir", "Afig una fila per a un color nou.", "secondary", self.afig_fila),
            ("Esborrar", "Esborra la fila triada.", "outline", self.esborra_fila),
            (
                "Pujar",
                "Mou la fila triada cap amunt (la primera és el document per defecte).",
                "outline",
                lambda: self.mou_fila(-1),
            ),
            (
                "Baixar",
                "Mou la fila triada cap avall.",
                "outline",
                lambda: self.mou_fila(1),
            ),
            (
                "Colors per defecte",
                "Torna a omplir la taula amb els colors de sempre.",
                "outline",
                self.restaura_colors,
            ),
        ):
            boto = QPushButton(text)
            boto.setProperty("class", estil)
            boto.setToolTip(consell)
            boto.clicked.connect(accio)
            colors_btns.addWidget(boto)
        colors_btns.addStretch()
        layout.addRow(colors_btns)

    def _seccio_documents(self, layout: QFormLayout) -> None:
        """Afig els recursos amb què es genera el document.

        Args:
            layout: Formulari on s'afegeixen les files.
        """
        layout.addRow(self._etiqueta_seccio("CONFIGURACIÓ DE DOCUMENTS"))

        # Estil CSS
        self.style_combo = QComboBox()
        self.load_styles()
        self._selecciona_recurs(self.style_combo, self.config.get("css_name", "prova.css"))

        self.template_combo = QComboBox()
        self.load_templates()
        self._selecciona_recurs(
            self.template_combo, self.config.get("template_name", "base.html")
        )

        self.script_combo = QComboBox()
        self.load_scripts()
        self._selecciona_recurs(
            self.script_combo, self.config.get("js_name", "script.js")
        )

        self.highlight_combo = QComboBox()
        for estil, etiqueta in ESTILS_RESSALTAT:
            # El text visible porta l'etiqueta; el valor desat és l'estil.
            self.highlight_combo.addItem(etiqueta, estil)
        self.highlight_combo.setToolTip(
            "El bloc de codi té fons fosc: els temes propis estan afinats "
            "per als llenguatges de classe (kotlin, java, bash, html, css, "
            "javascript, c++, c#, php)."
        )
        idx_h = self.highlight_combo.findData(
            self.config.get("highlight_style", ESTIL_RESSALTAT_DEFECTE)
        )
        if idx_h >= 0:
            self.highlight_combo.setCurrentIndex(idx_h)

        self.add_style_btn = self._boto_afig(self.import_style)
        layout.addRow(
            QLabel("Estil CSS:"), self._amb_boto(self.style_combo, self.add_style_btn)
        )

        # Plantilla HTML
        self.add_template_btn = self._boto_afig(self.import_template)
        layout.addRow(
            QLabel("Plantilla HTML:"),
            self._amb_boto(self.template_combo, self.add_template_btn),
        )

        # Script JS
        self.add_script_btn = self._boto_afig(self.import_script)
        layout.addRow(
            QLabel("Script JS:"), self._amb_boto(self.script_combo, self.add_script_btn)
        )

        # Estil de Codi (Highlight)
        layout.addRow(QLabel("Ressaltat de codi:"), self.highlight_combo)

        # Mode presentació (el document es reutilitza tal qual: vegeu
        # scripts/presentacio.js). Ací només es tria com comença.
        self.presentacio_nivell_combo = QComboBox()
        for etiqueta, nivell in (
            ("Cada ## (recomanat)", 2),
            ("Cada # (només títols)", 1),
            ("Cada ### (més granular)", 3),
        ):
            self.presentacio_nivell_combo.addItem(etiqueta, nivell)
        self.presentacio_nivell_combo.setToolTip(
            "Encapçalament que obri cada diapositiva. Amb ##, cada secció del "
            "document és una diapositiva; si no cap, es dividix tota sola."
        )
        idx_nivell = self.presentacio_nivell_combo.findData(
            self.config.get("presentacio_nivell", 2)
        )
        if idx_nivell >= 0:
            self.presentacio_nivell_combo.setCurrentIndex(idx_nivell)

        self.presentacio_modus_combo = QComboBox()
        self.presentacio_modus_combo.addItem(
            "Diapositives (dividix les seccions llargues)", "diapositives"
        )
        self.presentacio_modus_combo.addItem(
            "Scroll (seccions senceres, parada per secció)", "scroll"
        )
        self.presentacio_modus_combo.setToolTip(
            "En presentar-se pot canviar en directe amb la tecla M."
        )
        idx_modus = self.presentacio_modus_combo.findData(
            self.config.get("presentacio_modus", "diapositives")
        )
        if idx_modus >= 0:
            self.presentacio_modus_combo.setCurrentIndex(idx_modus)

        self.presentacio_tema_combo = QComboBox()
        self.presentacio_tema_combo.addItem("Fosc", "fosc")
        self.presentacio_tema_combo.addItem("Clar", "clar")
        self.presentacio_tema_combo.setToolTip(
            "Tema inicial del document (també a la presentació). Després es "
            "canvia amb el botó ☾ o la tecla T, i el navegador recorda "
            "l'elecció."
        )
        idx_tema = self.presentacio_tema_combo.findData(
            self.config.get("presentacio_tema", "clar")
        )
        if idx_tema >= 0:
            self.presentacio_tema_combo.setCurrentIndex(idx_tema)

        layout.addRow(QLabel("Presentació:"), self.presentacio_nivell_combo)
        layout.addRow(QLabel("Mode inicial:"), self.presentacio_modus_combo)
        layout.addRow(QLabel("Tema inicial:"), self.presentacio_tema_combo)

    @staticmethod
    def _boto_afig(accio) -> QPushButton:
        """Retorna el botó «+» que importa un recurs.

        Args:
            accio: Funció connectada al clic (obre el diàleg d'importació).

        Returns:
            El QPushButton quadrat amb l'estil secundari.
        """
        boto = QPushButton("+")
        boto.setFixedSize(30, 30)
        boto.setProperty("class", "secondary")
        boto.clicked.connect(accio)
        return boto

    @staticmethod
    def _selecciona_recurs(combo: QComboBox, nom: str) -> None:
        """Deixa triat el recurs desat a la configuració.

        Args:
            combo: Desplegable amb els recursos disponibles.
            nom: Nom del fitxer que s'ha de quedar triat.
        """
        index = combo.findText(nom)
        if index >= 0:
            combo.setCurrentIndex(index)

    def browse_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imatges (*.png *.jpg *.jpeg *.svg)")
        if file:
            self.logo_input.setText(file)

    # --- Taula de colors d'identitat ---

    def _crea_taula_colors(self) -> QTableWidget:
        """Crea la taula buida: una fila per color, curs i assignatura."""
        taula = QTableWidget(0, len(COLUMNES_COLORS_TAULA))
        taula.setHorizontalHeaderLabels(list(COLUMNES_COLORS_TAULA))
        taula.verticalHeader().setVisible(False)
        taula.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        taula.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        taula.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        taula.setToolTip(
            "Cada fila és un color amb el seu curs i la seua assignatura; la "
            "primera fila és el document per defecte."
        )
        capcalera = taula.horizontalHeader()
        capcalera.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        capcalera.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        capcalera.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        capcalera.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        taula.verticalHeader().setDefaultSectionSize(ALCADA_FILA_COLORS)
        return taula

    def _ajusta_alçada_taula(self) -> None:
        """Deixa a la taula l'alçada justa per a les files que té.

        Així no ocupa mitja pantalla quan hi ha dos colors i no creix sense
        límit quan n'hi ha molts: a partir de ``MAX_FILES_TAULA_VISIBLES`` la
        taula s'arrissa.
        """
        files = max(self.colors_table.rowCount(), 2)
        visibles = min(files, MAX_FILES_TAULA_VISIBLES)
        capcalera = max(self.colors_table.horizontalHeader().sizeHint().height(), 28)
        alcada = (
            capcalera
            + visibles * ALCADA_FILA_COLORS
            + 2 * self.colors_table.frameWidth()
        )
        self.colors_table.setFixedHeight(alcada)

    def _crea_combo(self, consell: str) -> QComboBox:
        """Crea un quadre combinat editable per al curs o l'assignatura.

        Args:
            consell: Text que descriu el camp (per al tooltip i el marcador).

        Returns:
            El quadre, amb una entrada buida i els suggeriments de la taula.
        """
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMinimumWidth(110)
        combo.setToolTip(
            f"{consell}: pots triar un valor dels que ja hi ha o escriure'n un de nou."
        )
        combo.addItem("")
        # Els suggeriments es refresquen en eixir del camp o en triar una opció
        # (mentre s'escriu no, per a no destorbar).
        combo.lineEdit().editingFinished.connect(self._refresca_suggeriments)
        combo.activated.connect(self._refresca_suggeriments)
        return combo

    def afig_fila(self, dades: dict | None = None, index: int | None = None) -> None:
        """Afig una fila a la taula amb el color, el curs i l'assignatura.

        Args:
            dades: Diccionari amb ``color`` (nom o hexadecimal; buit si encara
                no se n'ha triat cap), ``curs`` i ``assignatura``.
            index: Posició on s'inserix; ``None`` per a afegir-la al final.
        """
        dades = dades or {}
        text_color = str(dades.get("color") or "").strip()
        color = color_per_nom(text_color)
        posicio = self.colors_table.rowCount() if index is None else index
        self.colors_table.insertRow(posicio)

        camp_color = QLineEdit()
        camp_color.setPlaceholderText("Taronja o #c2410c")
        camp_color.setText(nom_curt_del_color(color) if color else text_color)
        camp_color.setToolTip(
            "Nom del color («Taronja») o hexadecimal («#c2410c»); la mostra de "
            "la dreta obri el selector de color."
        )
        camp_color.editingFinished.connect(
            lambda camp=camp_color: self._normalitza_camp_color(camp)
        )

        boto_mostra = QPushButton()
        boto_mostra.setProperty("class", "swatch")
        boto_mostra.setFixedSize(26, 26)
        boto_mostra.setCursor(Qt.CursorShape.PointingHandCursor)

        caixa_color = QWidget()
        fila_color = QHBoxLayout(caixa_color)
        fila_color.setContentsMargins(2, 2, 2, 2)
        fila_color.setSpacing(6)
        fila_color.addWidget(camp_color)
        fila_color.addWidget(boto_mostra)

        combo_curs = self._crea_combo("Curs")
        combo_curs.setEditText(str(dades.get("curs") or ""))
        combo_assig = self._crea_combo("Assignatura")
        combo_assig.setEditText(str(dades.get("assignatura") or ""))

        fila = {
            "color": camp_color,
            "mostra": boto_mostra,
            "curs": combo_curs,
            "assignatura": combo_assig,
        }
        self._files.insert(posicio, fila)
        self.colors_table.setCellWidget(posicio, 0, caixa_color)
        self.colors_table.setCellWidget(posicio, 1, combo_curs)
        self.colors_table.setCellWidget(posicio, 2, combo_assig)
        boto_mostra.clicked.connect(lambda: self._tria_color(fila))
        self._pinta_mostra(fila, color)
        self._ajusta_alçada_taula()

    def _ompli_taula(self, files: list[dict]) -> None:
        """Buida la taula i la torna a omplir amb les files indicades.

        Args:
            files: Una entrada per fila, amb ``color``, ``curs`` i
                ``assignatura`` (el color pot vindre com a nom o hexadecimal).
        """
        self.colors_table.setRowCount(0)
        self._files = []
        for dades in files:
            self.afig_fila(dades)
        self._refresca_suggeriments()
        self._ajusta_alçada_taula()

    def _fila_de(self, widget) -> dict | None:
        """Retorna la fila a què pertany un dels widgets de la taula."""
        for fila in self._files:
            if widget in fila.values():
                return fila
        return None

    def _pinta_mostra(self, fila: dict, color: str | None) -> None:
        """Pinta la mostra del color de la fila.

        Args:
            fila: Diccionari amb els widgets de la fila.
            color: Color hexadecimal, o ``None`` si el camp no té un color
                vàlid (aleshores la mostra queda buida i ratllada).
        """
        if color:
            fila["mostra"].setStyleSheet(
                f"background-color: {color}; border: 1px solid #d1d5db;"
                " border-radius: 6px;"
            )
            fila["mostra"].setToolTip(f"{nom_curt_del_color(color)} ({color})")
        else:
            fila["mostra"].setStyleSheet(
                "background-color: #e5e7eb; border: 1px dashed #9ca3af;"
                " border-radius: 6px;"
            )
            fila["mostra"].setToolTip("Encara no hi ha cap color triat")

    def _normalitza_camp_color(self, camp: QLineEdit) -> None:
        """Passa el text del camp de color a nom conegut o hexadecimal.

        Si el text no és cap color conegut, el camp queda marcat en roig perquè
        es corregisca abans de desar.

        Args:
            camp: Camp de text del color d'una fila.
        """
        text = camp.text().strip()
        color = color_per_nom(text)
        if color:
            camp.setText(nom_curt_del_color(color))
            camp.setStyleSheet("")
        else:
            camp.setStyleSheet("border: 1px solid #dc2626;" if text else "")

        fila = self._fila_de(camp)
        if fila is not None:
            self._pinta_mostra(fila, color)

    def _tria_color(self, fila: dict) -> None:
        """Obri el selector de color i l'aplica a la fila.

        Args:
            fila: Diccionari amb els widgets de la fila.
        """
        actual = QColor(color_per_nom(fila["color"].text()) or "#ffffff")
        color = QColorDialog.getColor(actual, self, "Color d'identitat")
        if not color.isValid():
            return
        fila["color"].setText(nom_curt_del_color(color.name()))
        fila["color"].setStyleSheet("")
        self._pinta_mostra(fila, color.name())

    def _valors_distints(self, clau: str) -> list[str]:
        """Retorna els valors ja escrits en una columna, sense repetir-los.

        Args:
            clau: ``"curs"`` o ``"assignatura"``.

        Returns:
            Els valors en l'orde en què apareixen a la taula.
        """
        valors: list[str] = []
        for fila in self._files:
            text = fila[clau].currentText().strip()
            if text and text not in valors:
                valors.append(text)
        return valors

    def _refresca_suggeriments(self, *_args) -> None:
        """Actualitza els suggeriments dels combos amb els valors de la taula."""
        if self._refresc:
            return
        self._refresc = True
        try:
            suggeriments = {
                clau: self._valors_distints(clau) for clau in ("curs", "assignatura")
            }
            for fila in self._files:
                for clau, valors in suggeriments.items():
                    combo = fila[clau]
                    text = combo.currentText()
                    posicio = combo.lineEdit().cursorPosition()
                    combo.blockSignals(True)
                    combo.clear()
                    combo.addItem("")
                    combo.addItems(valors)
                    combo.setEditText(text)
                    combo.lineEdit().setCursorPosition(min(posicio, len(text)))
                    combo.blockSignals(False)
        finally:
            self._refresc = False

    def esborra_fila(self, *_args) -> None:
        """Esborra la fila triada (si no n'hi ha cap triada, l'última)."""
        if not self._files:
            return
        index = self.colors_table.currentRow()
        if index < 0:
            index = len(self._files) - 1
        self.colors_table.removeRow(index)
        del self._files[index]
        self._refresca_suggeriments()
        self._ajusta_alçada_taula()

    def mou_fila(self, delta: int) -> None:
        """Mou la fila triada ``delta`` posicions amunt (negatiu) o avall.

        Args:
            delta: ``-1`` per a pujar-la i ``1`` per a baixar-la.
        """
        origen = self.colors_table.currentRow()
        desti = origen + delta
        if origen < 0 or not 0 <= desti < len(self._files):
            return
        files = self._dades_files()
        files[origen], files[desti] = files[desti], files[origen]
        self._ompli_taula(files)
        self.colors_table.selectRow(desti)

    def restaura_colors(self, *_args) -> None:
        """Torna a omplir la taula amb els colors per defecte."""
        self._ompli_taula(presets_per_defecte())

    def _dades_files(self) -> list[dict]:
        """Retorna el que hi ha escrit a cada fila, encara sense validar-ho."""
        return [
            {
                "color": fila["color"].text().strip(),
                "curs": fila["curs"].currentText().strip(),
                "assignatura": fila["assignatura"].currentText().strip(),
            }
            for fila in self._files
        ]

    def _identitats_de_la_taula(self) -> tuple[list[dict], list[str]]:
        """Convertix les files de la taula en la llista d'identitats del JSON.

        Les files completament buides s'ignoren; una fila amb curs o
        assignatura però sense color és un error, i també ho és un color que no
        es reconeix (ni nom conegut ni hexadecimal).

        Returns:
            Una tupla ``(identitats, errors)``: les identitats netes i sense
            duplicats, i un text per cada fila que cal corregir.
        """
        identitats: list[dict] = []
        errors: list[str] = []
        for numero, dades in enumerate(self._dades_files(), start=1):
            text_color = dades["color"]
            if not (text_color or dades["curs"] or dades["assignatura"]):
                continue
            color = color_per_nom(text_color)
            if color is None:
                if text_color:
                    errors.append(
                        f"fila {numero}: «{text_color}» no és un color conegut"
                    )
                else:
                    errors.append(f"fila {numero}: falta el color")
                continue
            identitats.append(
                {
                    "color": color,
                    "curs": dades["curs"],
                    "assignatura": dades["assignatura"],
                }
            )
        return normalitza_identitats(identitats), errors

    def load_styles(self):
        self.style_combo.clear()
        self.style_combo.addItems(
            recursos_disponibles(
                directoris_de_recurs("styles"), ".css", CSS_NO_SELECCIONABLES
            )
        )

    def load_templates(self):
        self.template_combo.clear()
        self.template_combo.addItems(
            recursos_disponibles(
                directoris_de_recurs("templates"), ".html", frozenset()
            )
        )

    def load_scripts(self):
        self.script_combo.clear()
        self.script_combo.addItems(
            recursos_disponibles(
                directoris_de_recurs("scripts"), ".js", JS_NO_SELECCIONABLES
            )
        )

    def import_style(self):
        self.import_resource("styles", "*.css", "Estil CSS", self.load_styles, self.style_combo)

    def import_template(self):
        self.import_resource("templates", "*.html", "Plantilla HTML", self.load_templates, self.template_combo)

    def import_script(self):
        self.import_resource("scripts", "*.js", "Script JS", self.load_scripts, self.script_combo)

    def import_resource(self, target_dir, file_filter, resource_name, refresh_callback, combo):
        file, _ = QFileDialog.getOpenFileName(self, f"Importar {resource_name}", "", f"{resource_name} ({file_filter})")
        if not file: return

        # Els recursos importats són dades de l'usuari: van a DATA_ROOT, perquè
        # el paquet pot ser de només lectura (AppImage, /usr/lib).
        dest_dir = from_data_root(target_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / Path(file).name

        if dest_path.exists():
            reply = QMessageBox.question(self, "Substituir", f"El fitxer '{dest_path.name}' ja existeix. Vols substituir-lo?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return

        try:
            shutil.copy(file, dest_path)
            refresh_callback()
            index = combo.findText(dest_path.name)
            if index >= 0: combo.setCurrentIndex(index)
            QMessageBox.information(self, "Èxit", f"{resource_name} importat correctament.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No s'ha pogut importar el recurs: {str(e)}")

    def save_config(self):
        # Cada fila de la taula és un color amb el seu curs i la seua
        # assignatura: ací es convertixen en la llista que es desa al JSON.
        identitats, errors = self._identitats_de_la_taula()
        if errors:
            detall = "\n".join(f"  · {error}" for error in errors)
            QMessageBox.warning(
                self,
                "Colors d'identitat",
                "No s'ha desat res perquè hi ha files que cal corregir:\n\n"
                f"{detall}\n\nEscriu un nom conegut o un color hexadecimal "
                "com «#c2410c».",
            )
            return
        if not identitats:
            QMessageBox.warning(
                self,
                "Colors d'identitat",
                "Cal almenys un color: la finestra principal sempre n'ha de "
                "mostrar un de triat. Escriu, per exemple, «Taronja» a la "
                "primera fila.",
            )
            return

        new_config = {
            "institut_nom": self.nom_input.text(),
            "institut_logo": self.logo_input.text(),
            "professor": self.prof_input.text(),
            "departament": self.dept_input.text(),
            # Cada color porta el seu curs i la seua assignatura: és el que fa
            # que en triar-lo a la finestra s'omplin eixos camps. El primer és
            # el document per defecte.
            "identitats": identitats,
            "css_name": self.style_combo.currentText(),
            "template_name": self.template_combo.currentText(),
            "js_name": self.script_combo.currentText(),
            "highlight_style": self.highlight_combo.currentData(),
            # Mode presentació: comença així i després es pot canviar amb M/T.
            "presentacio_nivell": self.presentacio_nivell_combo.currentData(),
            "presentacio_modus": self.presentacio_modus_combo.currentData(),
            "presentacio_tema": self.presentacio_tema_combo.currentData(),
        }
        save_institut_config(new_config)
        QMessageBox.information(self, "Guardat", "S'ha desat la configuració del projecte.")
        self.accept()

