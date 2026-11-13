"""Tests de la plantilla HTML i del script de suport.

Comproven invariants que afecten la validesa de l'HTML generat (ids duplicats
del sumari) i el ressaltat de codi (el fa pandoc, no highlight.js).
"""
import unittest

from src.infrastructure.project_paths import from_project_root


class TestBaseTemplate(unittest.TestCase):
    """Comprova la plantilla templates/base.html."""

    def setUp(self):
        self.plantilla = from_project_root("templates", "base.html").read_text(
            encoding="utf-8"
        )

    def test_toc_apareix_una_sola_vegada(self):
        """El $toc$ s'ha de generar una única vegada (barra lateral).

        L'índex d'impressió es clona per JS perquè, si es generara dos cops amb
        pandoc, els ids ``toc-*`` quedarien duplicats al DOM.
        """
        self.assertEqual(self.plantilla.count("$toc$"), 1)

    def test_injecta_el_css_de_ressaltat_de_pandoc(self):
        """Cal incloure $highlighting-css$ i abans del full d'estil propi."""
        self.assertIn("$highlighting-css$", self.plantilla)
        self.assertLess(
            self.plantilla.index("$highlighting-css$"),
            self.plantilla.index('href="$css$"'),
        )

    def test_no_carrega_highlight_js(self):
        """Ja no s'ha de carregar highlight.js (ho fa pandoc)."""
        self.assertNotIn("highlight.min.js", self.plantilla)

    def test_sense_enllacos_de_preconnexio(self):
        """L'HTML es carrega des de file://: el preconnect no fa res útil."""
        self.assertNotIn('rel="preconnect"', self.plantilla)
        self.assertIn("fonts.googleapis.com/css2", self.plantilla)

    def test_publica_les_variables_doc(self):
        """La plantilla ha de publicar les metadades com a variables --doc-*."""
        for variable in (
            "--doc-institut",
            "--doc-departament",
            "--doc-assignatura",
            "--doc-curs",
            "--doc-data",
        ):
            self.assertIn(variable, self.plantilla)


class TestPrintStyles(unittest.TestCase):
    """Comprova les regles d'impressió/PDF de styles/prova.css."""

    def setUp(self):
        self.css = from_project_root("styles", "prova.css").read_text(encoding="utf-8")

    def test_portada_i_index_samaguen_nomes_en_pantalla(self):
        """Les regles que amaguen portada/índex han de viure dins @media screen.

        Si s'apliquen també en imprimir, la portada i l'índex no s'imprimeixen.
        """
        bloc = self.css[self.css.index("@media screen {"):self.css.index("@media print {")]
        self.assertIn(".pdf-cover", bloc)
        self.assertIn(".pdf-toc", bloc)

    def test_capcalera_de_pantalla_oculta_en_imprimir(self):
        """En imprimir, la capçalera gran de pantalla no s'ha de mostrar."""
        bloc = self.css[self.css.index("@media print {"):]
        self.assertIn("Capçalera de pantalla: FORA de la impressió", bloc)
        seccio = bloc[bloc.index("Capçalera de pantalla"):][:400]
        self.assertRegex(seccio, r"\.header,[\s\S]*?display:\s*none !important")

    def test_capcaleres_i_peus_de_pagina(self):
        """@page ha de portar capçaleres/peus amb les variables --doc-*."""
        self.assertIn("@page {", self.css)
        self.assertIn("content: var(--doc-institut)", self.css)
        self.assertIn("content: var(--doc-departament)", self.css)
        self.assertIn('counter(page) " de " counter(pages)', self.css)

    def test_portada_sense_marges_ni_peus(self):
        """@page:first (portada) no ha de portar marges ni capçaleres."""
        bloc = self.css[self.css.index("@page:first"):]
        self.assertIn("margin: 0", bloc)
        self.assertIn("content: none", bloc)

    def test_paginacio_evita_talls_dolents(self):
        """Cal controlar vídues/òrfenes i repetir la capçalera de les taules."""
        self.assertIn("orphans: 3", self.css)
        self.assertIn("widows: 3", self.css)
        self.assertIn("display: table-header-group", self.css)


class TestCssCodi(unittest.TestCase):
    """Comprova les regles de codi de styles/base.css i styles/prova.css.

    Pandoc genera els blocs de codi com ``<pre class="sourceCode"><code
    class="sourceCode">`` amb un ``<span>`` per token, i els colors de cada
    token els injecta ``--highlight-style`` ($highlighting-css$). Si la regla
    de codi inline no s'exclou dels blocs, el color primari s'hereta a tot el
    bloc i el ressaltat no es veu.
    """

    def setUp(self):
        self.base = from_project_root("styles", "base.css").read_text(encoding="utf-8")
        self.prova = from_project_root("styles", "prova.css").read_text(encoding="utf-8")

    def test_el_codi_inline_exclou_els_blocs(self):
        """La regla de codi inline no pot ser un `code { }` sense qualificar."""
        self.assertIn(":not(pre) > code {", self.base)
        self.assertNotRegex(self.base, r"(?m)^code \{")

    def test_el_text_sense_token_hereta_el_color_del_bloc(self):
        """El text del bloc que pandoc no embolcalla ha de ser clar, no primari."""
        bloc = self.base[self.base.index("pre code {"):]
        bloc = bloc[:bloc.index("}")]
        self.assertIn("color: inherit", bloc)
        self.assertIn("background: transparent", bloc)

    def test_la_impressio_conserva_els_colors_dels_tokens(self):
        """En imprimir cal conservar el fons del bloc i el color del text."""
        impressio = self.prova[self.prova.index("@media print {"):]
        self.assertIn("print-color-adjust: exact", impressio)
        self.assertIn("-webkit-print-color-adjust: exact", impressio)
        self.assertRegex(impressio, r"pre code \{[^}]*color: inherit !important")

    def test_el_codi_llarg_es_parteix_en_paper(self):
        """Pandoc fixa `white-space: pre` al <code>: si no es canvia, les
        línies llargues s'ixen del bloc i el text clar cau sobre paper blanc."""
        impressio = self.prova[self.prova.index("@media print {"):]
        self.assertRegex(
            impressio,
            r"pre > code\.sourceCode \{[^}]*white-space: pre-wrap",
        )

    def test_les_linies_de_pandoc_hereten_el_nostre_interlineat(self):
        """Pandoc posa `line-height: 1.25` als spans de línia; el disseny
        (base.css) usa 1.7 i cal mantindre'l."""
        self.assertRegex(
            self.base,
            r"div\.sourceCode pre > code > span \{[^}]*line-height: inherit",
        )

    def test_les_consultes_de_mitja_de_pantalla_son_explícites(self):
        """Cap regla responsive sense `screen`: en paper no ha de canviar res."""
        self.assertNotIn("@media (max-width", self.prova)
        self.assertIn("@media screen and (max-width", self.prova)


class TestScriptJs(unittest.TestCase):
    """Comprova scripts/script.js."""

    def setUp(self):
        self.script = from_project_root("scripts", "script.js").read_text(
            encoding="utf-8"
        )

    def test_no_usa_highlight_js(self):
        """El script no ha de cridar hljs."""
        self.assertNotIn("hljs", self.script)

    def test_clona_el_sumari_traent_els_ids(self):
        """La còpia de l'índex per a impressió s'ha de fer sense ids."""
        self.assertIn(".pdf-toc .toc", self.script)
        self.assertIn("removeAttribute('id')", self.script)

    def test_els_desplegables_nomes_afecten_la_barra_lateral(self):
        """Els toggles del sumari només s'han d'aplicar al sidebar."""
        self.assertIn("'.sidebar .toc li'", self.script)

    def test_conserva_els_spans_del_ressaltat(self):
        """El JS no ha de reconstruir el bloc de codi.

        Si reemplaçara el contingut del <code> pel seu text (com es feia per a
        highlight.js), el bloc perdria els colors de --highlight-style i tot el
        codi quedaria d'un sol color, el del <pre>. Sí que pot afegir-hi spans
        dins, però mai reescriure l'element sencer.
        """
        self.assertNotIn("code.innerHTML", self.script)
        self.assertNotIn("code.textContent", self.script)
        self.assertNotIn("code.innerText =", self.script)

    def _bloc_llenguatges(self):
        """Retorna el contingut del Set LLENGUATGES_AMB_CRIDES."""
        inici = self.script.index("LLENGUATGES_AMB_CRIDES = new Set([")
        fi = self.script.index("]);", inici)
        return self.script[inici:fi]

    def test_ressalta_les_crides_amb_la_classe_fu(self):
        """Una crida que pandoc no pinta (`Column(`, `println(`) ha de dur `fu`.

        Pandoc (skylighting) no té informació semàntica: en Kotlin, Java o
        JavaScript deixa sense color els identificadors que són crides, i en
        codi de Jetpack Compose són les paraules més visibles.
        """
        self.assertIn("function marcaCrides(", self.script)
        self.assertIn("marcaCrides(code, lang)", self.script)
        self.assertIn("if (esCrida(text, m.index, m[1].length, node)) return 'fu';", self.script)

    def test_ressalta_els_tipus_amb_la_classe_dt(self):
        """Un tipus que pandoc deixa pla (`Modifier`, `Arrangement`) ha de dur `dt`.

        Sense això, `modifier: Modifier = Modifier` pinta el tipus de la
        declaració (que sí que reconeix pandoc) i deixa blanc el de
        l'expressió, i queden dos colors per a la mateixa paraula.
        """
        self.assertIn("function esTipus(", self.script)
        self.assertIn("if (esTipus(m[1], text, m.index, node)) return 'dt';", self.script)
        # Les constants (MAX_SIZE) i els membres (Arrangement.Center) no ho són.
        self.assertIn("/^[A-Z]/", self.script)
        self.assertIn("/[a-z]/", self.script)
        self.assertIn("anterior !== '.'", self.script)

    def test_no_toca_els_tokens_que_ja_pinta_pandoc(self):
        """Els textos dins d'un <span class="…"> no s'han de tocar."""
        self.assertIn("closest('span[class], a')", self.script)

    def test_les_crides_nomes_en_llenguatges_amb_crides(self):
        """`nom(` no és una crida en HTML, CSS ni bash: no s'hi ha d'activar."""
        bloc = self._bloc_llenguatges()
        for llenguatge in ("kotlin", "java", "javascript", "typescript",
                           "cpp", "cs", "php", "python"):
            self.assertIn(f"'{llenguatge}'", bloc)
        for llenguatge in ("html", "css", "bash", "sql"):
            self.assertNotIn(f"'{llenguatge}'", bloc)

    def test_les_paraules_clau_no_es_pinten_com_a_crides(self):
        """`if (` o `return (` no són crides encara que porten parèntesi."""
        self.assertIn("NO_SON_CRIDES", self.script)
        inici = self.script.index("NO_SON_CRIDES = new Set([")
        fi = self.script.index("]);", inici)
        bloc = self.script[inici:fi]
        for paraula in ("'if'", "'for'", "'while'", "'return'", "'new'"):
            self.assertIn(paraula, bloc)

    def test_la_barra_dels_blocs_sense_llenguatge_queda_fora_del_pre(self):
        """Els blocs que pandoc no ressalta (`text`) no van dins de cap <div>.

        Pandoc deixa un `<pre class="text">` solt, sense el `div.sourceCode`
        que embolcalla els blocs ressaltats. Si la barra s'inseria dins del
        <pre>, quedava dins del seu padding: sagnada respecte del bloc, més
        curta que la seua vora i amb la tipografia del codi. El JS ha de crear
        el mateix embolcall perquè tots els blocs es vegen igual.
        """
        self.assertIn("container.className = 'sourceCode'", self.script)
        self.assertIn("pre.replaceWith(container)", self.script)
        self.assertIn("container.appendChild(pre)", self.script)
        # La barra sempre va al contenidor, mai dins del <pre>.
        self.assertIn(
            "container.insertBefore(header, container.firstChild)", self.script
        )
        self.assertNotIn("pre.insertBefore(", self.script)

    def test_letiqueta_usa_el_llenguatge_declarat_al_pre(self):
        """Un ```foobar: pandoc posa la classe al <pre> i l'etiqueta l'ha de vore.

        Sense eixa caiguda, qualsevol bloc que pandoc no ressalta (també
        `text`) s'etiquetava sempre com a TEXT i s'amagava el llenguatge que
        havia escrit l'usuari.
        """
        self.assertIn("CLASSES_DE_PANDOC", self.script)
        self.assertIn("Array.from(pre.classList).find(", self.script)
        for classe in ("'sourceCode'", "'numberLines'", "'numberSource'",
                       "'lineAnchors'"):
            self.assertIn(classe, self.script)

    def test_highlight_min_js_esborrat(self):
        """La llibreria highlight.js (121 KB) ja no ha d'existir."""
        self.assertFalse(from_project_root("scripts", "highlight.min.js").exists())


class TestPresentacio(unittest.TestCase):
    """Comprova els ganxos del mode presentació (plantilla, CSS i JS)."""

    def setUp(self):
        self.plantilla = from_project_root("templates", "base.html").read_text(
            encoding="utf-8"
        )
        self.script = from_project_root("scripts", "presentacio.js").read_text(
            encoding="utf-8"
        )
        self.css = from_project_root("styles", "presentacio.css").read_text(
            encoding="utf-8"
        )

    def test_la_plantilla_te_el_boto_i_el_script(self):
        """El botó ▶ i el script s'inclouen només si el recurs hi és."""
        self.assertIn('id="presentacio-toggle"', self.plantilla)
        self.assertIn("$if(presentacio_js)$", self.plantilla)
        self.assertIn('src="$presentacio_js$"', self.plantilla)

    def test_el_script_va_despres_de_mermaid(self):
        """El script espera els diagrames: mermaid s'ha de carregar abans."""
        self.assertLess(
            self.plantilla.index("mermaid.min.js"),
            self.plantilla.index('src="$presentacio_js$"'),
        )

    def test_la_plantilla_publica_la_configuracio(self):
        """El body ha de dur el nivell, el mode i el tema com a data-*."""
        for clau in ("presentacio_nivell", "presentacio_modus", "presentacio_tema"):
            atribut = clau.replace("_", "-")
            self.assertIn(f'data-{atribut}="$' + clau + '$"', self.plantilla)

    def test_el_css_nomes_actua_en_mode_presentacio(self):
        """La vista normal i el PDF no han de canviar."""
        self.assertIn("body.mode-presentacio {", self.css)
        self.assertIn("body.mode-presentacio .content {", self.css)
        # L'amagat de la interfície ha de véncer l'estil triat.
        self.assertIn("display: none !important", self.css)

    def test_el_css_samaga_en_imprimir(self):
        """Si s'imprimeix sense desmuntar, la interfície no ha d'eixir al paper."""
        bloc = self.css[self.css.index("@media print {"):]
        for clase in ("presentacio-barra", "presentacio-peu", "presentacio-ajuda-panel"):
            self.assertIn(clase, bloc)

    def test_el_script_mou_els_nodes_i_els_restaura(self):
        """No es clona el document: es mouen els nodes i es tornen a posar."""
        self.assertIn("Array.from(contingut.childNodes)", self.script)
        self.assertIn("contingut.replaceChildren(...(originals || []))", self.script)

    def test_les_continuacions_no_dupliquen_identificadors(self):
        """Els títols de continuació es clonen sense id (HTML vàlid)."""
        self.assertIn("clon.removeAttribute('id')", self.script)
        self.assertIn("querySelectorAll('[id]')", self.script)

    def test_el_nivell_de_tall_ix_de_la_configuracio(self):
        """El nivell (## per defecte) no s'ha de fixar al codi."""
        self.assertIn("dataset.presentacioNivell", self.script)
        self.assertIn("'h' + NIVELL", self.script)

    def test_el_titol_de_la_diapositiva_va_centrat(self):
        """El títol va centrat, sense la barra vertical del h2 del cos."""
        bloc = self.css[
            self.css.index(".content .slide-titol {") :
            self.css.index(".content .slide-portada .slide-titol {")
        ]
        self.assertIn("text-align: center;", bloc)
        self.assertIn("padding-left: 0;", bloc)
        # La barra de h2::before només cau amb `content: none` (base.css usa
        # `display: block !important`).
        self.assertIn("content: none;", bloc)
        # La línia de base és simètrica, com la de la portada.
        self.assertRegex(bloc, r"left:\s*10%;\s*width:\s*80%;")
        # El rètol de context també va centrat, i no calen excepcions per a
        # la portada: era l'únic títol que ja anava centrat.
        rotul = self.css[
            self.css.index(".content .slide-rotul {") :
            self.css.index(".content .slide-titol {")
        ]
        self.assertIn("text-align: center;", rotul)
        self.assertNotIn(".slide-portada .slide-titol::after", self.css)
        self.assertNotIn(".slide-portada .slide-rotul", self.css)

    def test_el_peu_te_icones_en_compte_de_glifs(self):
        """Els botons del peu són SVG; ni M ni T ni ⛶ es repetixen ahí."""
        inici = self.script.index("const ICONES = {")
        bloc = self.script[inici : self.script.index("};", inici)]
        self.assertEqual(bloc.count("<svg"), 4)
        for clau in ("anterior", "seguent", "ajuda", "eixir"):
            self.assertIn(clau + ":", bloc)
            self.assertIn("creaBoto('" + clau + "'", self.script)
        for glif in ("M", "T", "⛶", "◀", "▶", "✕"):
            self.assertNotIn("creaBoto('" + glif + "'", self.script)
        self.assertIn("presentacio-boto-icona", self.css)

    def test_cap_encapcalament_no_queda_sol_en_tallar(self):
        """El tall d'una diapositiva mai no deixa un títol orfe al final."""
        self.assertIn("SELECTOR_ENCAPCALAMENT", self.script)
        self.assertIn("esEncapcalament(fills[tall - 1]) ? -1 : tall", self.script)
        self.assertIn("if (tall < 1) break;", self.script)


class TestTema(unittest.TestCase):
    """Hi ha un sol tema (clar/fosc) per a tota la pàgina.

    La paleta viu a base.css (``html.tema-fosc``) i la compartixen la vista
    normal i la presentació: la presentació només canvia la disposició. La
    preferència es desa al navegador i s'aplica abans del primer pintat.
    """

    def setUp(self):
        self.plantilla = from_project_root("templates", "base.html").read_text(
            encoding="utf-8"
        )
        self.base = from_project_root("styles", "base.css").read_text(encoding="utf-8")
        self.presentacio_css = from_project_root(
            "styles", "presentacio.css"
        ).read_text(encoding="utf-8")
        self.script = from_project_root("scripts", "script.js").read_text(
            encoding="utf-8"
        )
        self.presentacio_js = from_project_root(
            "scripts", "presentacio.js"
        ).read_text(encoding="utf-8")

    def test_la_paleta_fosca_es_unica(self):
        """El fosc es definix una sola vegada, a <html>, i no a la presentació."""
        self.assertIn("html.tema-fosc {", self.base)
        self.assertIn("--color-fons: #0b1220;", self.base)
        # La presentació no pot tindre paleta pròpia: només disposició.
        self.assertNotIn("--color-fons:", self.presentacio_css)
        self.assertNotIn("tema-clar", self.presentacio_css)

    def test_la_preferencia_s_aplica_abans_de_pintar(self):
        """L'script del <head> evita el flaix clar→fosc al recarregar."""
        self.assertIn("markdownstyler-tema", self.plantilla)
        self.assertIn(
            "document.documentElement.classList.add('tema-fosc')", self.plantilla
        )
        self.assertLess(
            self.plantilla.index("markdownstyler-tema"),
            self.plantilla.index('href="$css$"'),
        )

    def test_el_boto_de_tema_es_de_la_barra(self):
        """El botó ☾ forma part de la fila flotant i, en presentació, passa a
        la cantonada (al peu no hi ha cap botó de tema) i no ix en paper."""
        self.assertIn('id="tema-toggle"', self.plantilla)
        self.assertIn("#tema-toggle", self.base)
        self.assertIn("body.mode-presentacio #tema-toggle", self.presentacio_css)
        bloc = self.presentacio_css[self.presentacio_css.index("@media print {"):]
        self.assertIn("#tema-toggle", bloc)

    def test_la_fila_de_botons_ix_de_les_mides(self):
        """Afegir un botó nou només ha de ser sumar una --toggle-mida."""
        self.assertIn("--toggle-mida: 40px;", self.base)
        self.assertIn("--toggle-marge: 15px;", self.base)
        self.assertIn(
            "calc(var(--toggle-marge) + 3 * var(--toggle-mida))", self.base
        )
        # El ▶ és el quart per la dreta; el seu offset el fixa presentacio.css.
        self.assertIn(
            "calc(var(--toggle-marge) + 3 * var(--toggle-mida))",
            self.presentacio_css,
        )

    def test_el_paper_surt_sempre_en_clar(self):
        """En imprimir es recuperen els colors del paper encara que estiga fosc."""
        bloc = self.base[self.base.index("@media print {"):]
        self.assertIn("html.tema-fosc", bloc)
        self.assertIn("--color-superficie: #ffffff;", bloc)

    def test_el_script_compartix_l_api_del_tema(self):
        """Un sol lloc decideix el tema: MSTema (script.js)."""
        self.assertIn("window.MSTema", self.script)
        self.assertIn("markdownstyler-tema", self.script)
        for metode in ("actual()", "preferencia()", "aplica(", "aplicaPreferencia(", "alterna()"):
            self.assertIn(metode, self.script)
        # La presentació delega i no guarda tema propi.
        self.assertIn("window.MSTema.alterna()", self.presentacio_js)
        self.assertNotIn("TEMA_CONFIG", self.presentacio_js)
        self.assertNotIn("tema-clar", self.presentacio_js)


if __name__ == "__main__":
    unittest.main()
