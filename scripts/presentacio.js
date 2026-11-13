/* =========================================================================
   MODE PRESENTACIÓ
   =========================================================================
   Converteix el document ja generat en una presentació, sense demanar cap
   marcador especial al Markdown:

     · Agrupa els fills de `.content` per encapçalament de nivell N (per
       defecte els `##`) i cada grup es convertix en una diapositiva.
     · Les diapositives viuen DINS del mateix `.content`, que passa a ocupar
       la pantalla. Així no es clona res: diagrames, fórmules, codi i
       identificadors es conserven tal qual, i els estils de l'estil triat
       continuen funcionant.
     · Si una secció no cap en una pantalla, es dividix per blocs sencers,
       preferint tallar davant d'un encapçalament (així el títol de l'apartat
       i el seu contingut van junts); si no hi ha cap tall net, la diapositiva
       es deixa amb scroll intern. Cap títol no es queda sol al final.
     · En eixir es restaura el document original, node a node.

   Activat amb P/F5 o amb el botó ▶ de la capçalera; vegeu la llista de tecles
   al panell d'ajuda (?).
   ========================================================================= */
(function () {
    'use strict';

    const body = document.body;
    const contingut = document.querySelector('.content');
    if (!contingut) return;

    // --- Configuració que arriba de la plantilla ------------------------
    const NIVELL = Math.min(
        6,
        Math.max(1, parseInt(body.dataset.presentacioNivell, 10) || 2)
    );
    const MODUS_CONFIG =
        body.dataset.presentacioModus === 'scroll' ? 'scroll' : 'diapositives';

    const SELECTOR_TITOL = 'h' + NIVELL;
    // Qualsevol encapçalament del cos (sempre de nivell més fondo que NIVELL):
    // servix per a decidir on es pot tallar una diapositiva.
    const SELECTOR_ENCAPCALAMENT = 'h1, h2, h3, h4, h5, h6';
    const CLAU_POSICIO = 'markdownstyler-presentacio:' + location.pathname;
    const SUAU = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const TEXT_AJUDES = '← → · F pantalla completa · T tema · ? ajuda';

    // --- Estat ----------------------------------------------------------
    let actiu = false;
    let mode = MODUS_CONFIG;
    let slides = [];
    let index = 0;
    let originals = null;
    let rotul = '';
    let barra = null;
    let progres = null;
    let peu = null;
    let comptador = null;
    let textAjuda = null;
    let panellAjuda = null;
    let temporitzadorMesura = 0;
    let temporitzadorScroll = 0;
    let temporitzadorGuardar = 0;

    // --- Utilitats ------------------------------------------------------

    const esElement = (node) => node.nodeType === Node.ELEMENT_NODE;
    const esTitol = (node) => esElement(node) && node.matches(SELECTOR_TITOL);

    /** Text net d'una variable CSS de metadades (--doc-curs, …). */
    function variable(id) {
        const valor = getComputedStyle(document.documentElement)
            .getPropertyValue(id)
            .trim();
        return valor.replace(/^"|"$/g, '').replace(/\\"/g, '"').trim();
    }

    /** Rètol de context: assignatura · curs (o el que hi haja). */
    function calculaRotul() {
        return [variable('--doc-assignatura'), variable('--doc-curs')]
            .filter(Boolean)
            .join(' · ');
    }

    /** Desa la posició per a la pròxima vegada (si el navegador ho permet). */
    function guardaPosicio() {
        clearTimeout(temporitzadorGuardar);
        temporitzadorGuardar = setTimeout(() => {
            try {
                localStorage.setItem(CLAU_POSICIO, String(index));
            } catch (error) {
                /* file:// o mode privat: no passa res */
            }
        }, 350);
    }

    /** Recupera la posició: primer el hash (#presentar/3) i després el desat. */
    function recuperaPosicio() {
        const hash = /^#presentar(?:\/(\d+))?$/.exec(location.hash);
        if (hash && hash[1]) return Math.max(0, parseInt(hash[1], 10) - 1);
        try {
            const desat = parseInt(localStorage.getItem(CLAU_POSICIO), 10);
            if (!isNaN(desat) && desat > 0) return desat;
        } catch (error) {
            /* sense emmagatzematge */
        }
        return 0;
    }

    /** Escriu el hash sense recarregar (a file:// replaceState pot fallar). */
    function escriuHash(text) {
        try {
            history.replaceState(null, '', text);
        } catch (error) {
            try {
                location.replace(text);
            } catch (error2) {
                /* res a fer */
            }
        }
    }


    // --- Agrupació del document -----------------------------------------

    /** Els fills originals que ens interessen (elements i text amb contingut). */
    function fillsOriginals() {
        return originals.filter(
            (node) =>
                esElement(node) ||
                (node.nodeType === Node.TEXT_NODE && node.textContent.trim())
        );
    }

    /**
     * Repartix el document en grups: un per cada encapçalament del nivell
     * triat. El primer pot ser la portada (contingut previ al primer títol).
     */
    function agrupa() {
        const grups = [];
        let actual = null;
        fillsOriginals().forEach((node) => {
            if (esTitol(node)) {
                actual = { titol: node, fills: [] };
                grups.push(actual);
                return;
            }
            // Els `---` del Markdown no fan falta ací: el full de presentació
            // ja separa les seccions.
            if (esElement(node) && node.matches('hr')) return;
            if (!actual) {
                actual = { titol: null, fills: [] };
                grups.push(actual);
            }
            actual.fills.push(node);
        });
        return grups;
    }

    /**
     * Crea una secció i l'afig al deck.
     *
     * Ha d'estar al DOM per poder-la mesurar abans de decidir si cal
     * fragmentar-la.
     */
    function creaSlide(opcions) {
        const { titol = null, cont = false, portada = false, grup = 0 } = opcions;
        const slide = document.createElement('section');
        slide.className = 'slide' + (portada ? ' slide-portada' : '');
        slide.dataset.grup = String(grup);
        slide.setAttribute('role', 'group');
        slide.setAttribute('aria-roledescription', 'diapositiva');

        if (rotul) {
            const linia = document.createElement('p');
            linia.className = 'slide-rotul';
            linia.textContent = rotul;
            slide.append(linia);
        }

        if (titol) {
            titol.classList.add('slide-titol');
            if (cont) {
                const marca = document.createElement('span');
                marca.className = 'slide-cont';
                marca.textContent = '(cont.)';
                titol.append(marca);
            }
            slide.append(titol);
        }

        const cos = document.createElement('div');
        cos.className = 'slide-cos';
        slide.append(cos);

        // Si la diapositiva fa scroll intern, el peu ha de saber-ho per a
        // mostrar «↓ continua».
        slide.addEventListener('scroll', () => {
            if (actiu) actualitzaEstat();
        });

        contingut.append(slide);
        slides.push(slide);
        return { slide, cos };
    }

    /** Una diapositiva desborda si el contingut no cap en la pantalla. */
    function desborda(slide) {
        return slide.scrollHeight > slide.clientHeight + 2;
    }

    /** Clon del títol sense identificadors (la resta, intacta). */
    function clonaTitol(titol) {
        if (!titol) return null;
        const clon = titol.cloneNode(true);
        clon.removeAttribute('id');
        clon.querySelectorAll('[id]').forEach((node) => node.removeAttribute('id'));
        const marca = clon.querySelector('.slide-cont');
        if (marca) marca.remove();
        return clon;
    }

    /** Lleva del deck una diapositiva de prova que no ha servit. */
    function descarta(slide) {
        const posicio = slides.indexOf(slide);
        if (posicio >= 0) slides.splice(posicio, 1);
        slide.remove();
    }

    /** Un encapçalament del cos (h1…h6). */
    const esEncapcalament = (node) => node.matches(SELECTOR_ENCAPCALAMENT);

    /**
     * Índex a partir del qual cal moure els fills a la següent diapositiva, o
     * -1 si no hi ha cap tall net (llavors la diapositiva fa scroll).
     *
     * Un tall és net si el que es queda no acaba amb un encapçalament: així
     * cap títol no es queda sol al final d'una diapositiva. Entre els talls
     * possibles es preferix el que comença en un encapçalament, de manera que
     * el títol de l'apartat i el seu contingut passen junts a la següent.
     */
    function puntDeTall(cos) {
        const fills = Array.from(cos.children);
        for (let i = fills.length - 1; i >= 1; i -= 1) {
            if (!esEncapcalament(fills[i])) continue;
            // Una corrua d'encapçalaments (h3 seguit d'un h4 encara sense
            // text) va sencera: el primer tampoc no pot quedar-se sol.
            let tall = i;
            while (tall > 1 && esEncapcalament(fills[tall - 1])) tall -= 1;
            if (!esEncapcalament(fills[tall - 1])) return tall;
        }
        // Sense encapçalaments on tallar: baixa el darrer bloc, però mai
        // deixant un títol orfe al final de la diapositiva actual.
        const tall = fills.length - 1;
        return esEncapcalament(fills[tall - 1]) ? -1 : tall;
    }

    /** La portada: el h1 (si n'hi ha) i la resta de contingut inicial. */
    function muntaPortada(grup) {
        const h1 = grup.fills.find(
            (node) => esElement(node) && node.matches('h1')
        );
        const fills = grup.fills.filter((node) => node !== h1);
        const prova = creaSlide({ titol: h1 || null, portada: true, grup: 0 });
        prova.cos.append(...fills);

        if (!desborda(prova.slide) || mode === 'scroll') {
            if (desborda(prova.slide)) prova.slide.classList.add('desborda');
            return [prova.slide];
        }

        // Document sense seccions: es repartix pels blocs.
        descarta(prova.slide);
        return fragmentaBlocs({ titol: h1 || null, fills }, fills, 0, true);
    }

    /**
     * Repartix una llista de blocs en tantes diapositives com calga.
     *
     * Mai talla dins d'un bloc (taula, codi, figura): si un bloc sol no cap,
     * queda en una diapositiva amb scroll intern.
     */
    function fragmentaBlocs(grup, fills, indexGrup, esPrimera) {
        const resultat = [];
        let { slide, cos } = creaSlide({
            titol: esPrimera ? grup.titol : clonaTitol(grup.titol),
            cont: !esPrimera,
            grup: indexGrup,
        });
        resultat.push(slide);

        fills.forEach((node) => {
            cos.append(node);
            // Mentre no cap, es mou la cua a una diapositiva nova. El tall
            // preferix quedar davant d'un encapçalament; si no n'hi ha cap de
            // net, es deixa així (farà scroll) i s'espera al bloc següent.
            while (desborda(slide) && cos.children.length > 1) {
                const tall = puntDeTall(cos);
                if (tall < 1) break;
                const moguts = Array.from(cos.children).slice(tall);
                ({ slide, cos } = creaSlide({
                    titol: clonaTitol(grup.titol),
                    cont: true,
                    grup: indexGrup,
                }));
                resultat.push(slide);
                cos.append(...moguts);
            }
        });

        resultat.forEach((diapo) => {
            if (desborda(diapo)) diapo.classList.add('desborda');
        });
        return resultat;
    }

    /** Construeix totes les diapositives d'una secció (fragmentant si cal). */
    function muntaGrup(grup, indexGrup) {
        const prova = creaSlide({ titol: grup.titol, grup: indexGrup });
        prova.cos.append(...grup.fills);

        if (mode === 'scroll' || !desborda(prova.slide)) {
            if (desborda(prova.slide)) prova.slide.classList.add('desborda');
            return [prova.slide];
        }
        descarta(prova.slide);

        // Tall per blocs sencers, preferint quedar davant d'un apartat ###.
        return fragmentaBlocs(grup, grup.fills, indexGrup, true);
    }

    /** Buida el deck i el torna a construir amb el mode actual. */
    function munta() {
        slides = [];
        contingut.replaceChildren();
        agrupa().forEach((grup, indexGrup) => {
            if (indexGrup === 0 && !grup.titol) muntaPortada(grup);
            else muntaGrup(grup, indexGrup);
        });
    }



    // --- Navegació -------------------------------------------------------

    /** Si la diapositiva actual encara té contingut per davall. */
    function teScrollPendent(slide) {
        return (
            !!slide &&
            slide.scrollHeight - slide.scrollTop - slide.clientHeight > 6
        );
    }

    /** Va a una diapositiva concreta (sense passar-se'n dels límits). */
    function vésA(desti, opcions) {
        if (!slides.length) return;
        const suau = !opcions || opcions.suau !== false;
        index = Math.max(0, Math.min(slides.length - 1, desti));
        contingut.scrollTo({
            top: slides[index].offsetTop,
            behavior: suau && SUAU ? 'smooth' : 'auto',
        });
        actualitzaEstat();
        guardaPosicio();
        escriuHash('#presentar/' + (index + 1));
    }

    /**
     * Avança: primer acaba de recórrer la diapositiva (si en té de més) i
     * després passa a la següent.
     */
    function seguent() {
        if (!actiu) return;
        if (teScrollPendent(slides[index])) {
            slides[index].scrollBy({
                top: slides[index].clientHeight * 0.85,
                behavior: SUAU ? 'smooth' : 'auto',
            });
            return;
        }
        vésA(index + 1);
    }

    /** Retrocedix, amb la mateixa lògica que ``seguent``. */
    function anterior() {
        if (!actiu) return;
        const slide = slides[index];
        if (slide && slide.scrollTop > 6) {
            slide.scrollBy({
                top: -slide.clientHeight * 0.85,
                behavior: SUAU ? 'smooth' : 'auto',
            });
            return;
        }
        vésA(index - 1);
    }

    /** Actualitza comptador, barra i pista de continuació. */
    function actualitzaEstat() {
        if (!actiu || !slides.length || !comptador) return;
        const total = slides.length;
        comptador.textContent = index + 1 + ' / ' + total;
        progres.style.width = (((index + 1) / total) * 100).toFixed(2) + '%';
        textAjuda.textContent = teScrollPendent(slides[index])
            ? '↓ continua'
            : TEXT_AJUDES;
    }

    /** Seguix el scroll del deck per a mantindre índex, comptador i hash. */
    function enScroll() {
        if (!actiu) return;
        clearTimeout(temporitzadorScroll);
        temporitzadorScroll = setTimeout(() => {
            const mig = contingut.scrollTop + contingut.clientHeight / 2;
            let nou = 0;
            for (let i = 0; i < slides.length; i += 1) {
                if (slides[i].offsetTop <= mig) nou = i;
                else break;
            }
            index = nou;
            actualitzaEstat();
            guardaPosicio();
            escriuHash('#presentar/' + (index + 1));
        }, 90);
    }

    // --- Mode, tema i pantalla -------------------------------------------

    /** Alterna diapositives (amb fragmentació) i scroll (seccions senceres). */
    function canviaMode() {
        if (!actiu) return;
        mode = mode === 'diapositives' ? 'scroll' : 'diapositives';
        contingut.classList.toggle('presentacio-scroll', mode === 'scroll');
        reMesura();
    }

    /** Alterna el tema. No n'hi ha un de propi de la presentació: canvia el
        tema del document (MSTema, a script.js) i es desa per a la pròxima
        vegada, també per a la vista normal. */
    function canviaTema() {
        if (!actiu) return;
        if (window.MSTema) {
            window.MSTema.alterna();
        }
    }

    /** Entra o ix de pantalla completa sense tocar el mode. */
    function pantallaCompleta() {
        if (document.fullscreenElement) {
            document.exitFullscreen().catch(() => {});
            return;
        }
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(() => {});
        }
    }

    /**
     * Re-mesura diferida: en canviar la mida o entrar a pantalla completa,
     * les diapositives poden encabir-hi més (o menys) i cal tornar a repartir.
     */
    function programaReMesura() {
        clearTimeout(temporitzadorMesura);
        temporitzadorMesura = setTimeout(reMesura, 150);
    }

    function reMesura() {
        if (!actiu) return;
        const grup = slides[index] ? slides[index].dataset.grup : '0';
        munta();
        const desti = slides.findIndex((slide) => slide.dataset.grup === grup);
        vésA(desti >= 0 ? desti : Math.min(index, slides.length - 1), {
            suau: false,
        });
    }

    // --- Interfície (barra, peu i ajuda) -------------------------------

    /**
     * Icones del peu, en SVG en línia com les de la fila flotant de la
     * capçalera: el traç agafa el color del text (`currentColor`), així que
     * hereten el tema sense cap regla més. Els glifs de text (◀ ▶ ✕…) es
     * dibuixen distint en cada tipografia i quedaven desigualts.
     */
    const ICONES = {
        anterior:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<polyline points="15 18 9 12 15 6"></polyline></svg>',
        seguent:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<polyline points="9 18 15 12 9 6"></polyline></svg>',
        ajuda:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<circle cx="12" cy="12" r="10"></circle>' +
            '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>' +
            '<line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        eixir:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<line x1="18" y1="6" x2="6" y2="18"></line>' +
            '<line x1="6" y1="6" x2="18" y2="18"></line></svg>',
    };

    /**
     * Botó menut del peu. Si l'etiqueta és una clau d'ICONES el botó és només
     * la icona (el title i l'aria-label diuen què fa); si no, duu text.
     */
    function creaBoto(etiqueta, titol, accio) {
        const boto = document.createElement('button');
        boto.type = 'button';
        boto.className = 'presentacio-boto';
        boto.title = titol;
        boto.setAttribute('aria-label', titol);
        if (ICONES[etiqueta]) {
            boto.classList.add('presentacio-boto-icona');
            boto.innerHTML = ICONES[etiqueta];
        } else {
            boto.textContent = etiqueta;
        }
        boto.addEventListener('click', (event) => {
            event.preventDefault();
            accio();
        });
        return boto;
    }

    /** Taula de tecles del panell d'ajuda. */
    function creaPanellAjuda() {
        const panell = document.createElement('div');
        panell.className = 'presentacio-ajuda-panel';
        panell.hidden = true;
        panell.setAttribute('role', 'dialog');
        panell.setAttribute('aria-modal', 'true');
        panell.setAttribute('aria-labelledby', 'presentacio-ajuda-titol');

        const caixa = document.createElement('div');
        caixa.className = 'presentacio-ajuda-caixa';

        const titol = document.createElement('h2');
        titol.id = 'presentacio-ajuda-titol';
        titol.textContent = 'Mode presentació';

        const intro = document.createElement('p');
        intro.textContent =
            'El document sencer, en diapositives o en scroll. No cal cap ' +
            'marcador especial al Markdown.';

        const llista = document.createElement('dl');
        [
            ['→ ↓ Espai', 'Diapositiva o secció següent'],
            ['← ↑', 'Anterior'],
            ['Inici Fi', 'Primera o última'],
            ['M', 'Diapositives o scroll'],
            ['F', 'Pantalla completa'],
            ['T', 'Tema clar o fosc'],
            ['?', 'Esta ajuda'],
            ['Esc', 'Eixir'],
        ].forEach(([tecles, descripcio]) => {
            const dt = document.createElement('dt');
            tecles.split(' ').forEach((tecla) => {
                const kbd = document.createElement('kbd');
                kbd.textContent = tecla;
                dt.append(kbd, ' ');
            });
            const dd = document.createElement('dd');
            dd.textContent = descripcio;
            llista.append(dt, dd);
        });

        const tanca = document.createElement('button');
        tanca.type = 'button';
        tanca.className = 'presentacio-boto';
        tanca.textContent = 'Tanca';
        tanca.addEventListener('click', amagaAjuda);

        caixa.append(titol, intro, llista, tanca);
        panell.append(caixa);
        panell.addEventListener('click', (event) => {
            if (event.target === panell) amagaAjuda();
        });
        return panell;
    }

    /** Crea la barra de progrés i el peu amb comptador i botons. */
    function creaUI() {
        barra = document.createElement('div');
        barra.className = 'presentacio-barra';
        barra.setAttribute('aria-hidden', 'true');
        progres = document.createElement('span');
        barra.append(progres);

        peu = document.createElement('div');
        peu.className = 'presentacio-peu';
        textAjuda = document.createElement('span');
        textAjuda.className = 'presentacio-ajuda';
        comptador = document.createElement('span');
        comptador.className = 'presentacio-comptador';
        comptador.setAttribute('aria-live', 'polite');

        // Peu: comptador i quatre botons d'icona. El tema (☾/☀) i la pantalla
        // completa (⛶) no es repetixen ací: continuen a la cantonada superior
        // dreta, com en la vista normal (vegeu styles/presentacio.css).
        peu.append(
            textAjuda,
            comptador,
            creaBoto('anterior', 'Diapositiva anterior (←)', anterior),
            creaBoto('seguent', 'Diapositiva següent (→)', seguent),
            creaBoto('ajuda', 'Tecles de la presentació (?)', mostraAjuda),
            creaBoto('eixir', 'Eixir de la presentació (Esc)', desactiva)
        );

        panellAjuda = creaPanellAjuda();
        body.append(barra, peu, panellAjuda);
    }

    /** Lleva tota la interfície de presentació del document. */
    function llevaUI() {
        [barra, peu, panellAjuda].forEach((node) => {
            if (node) node.remove();
        });
        barra = null;
        progres = null;
        peu = null;
        comptador = null;
        textAjuda = null;
        panellAjuda = null;
    }

    function mostraAjuda() {
        if (panellAjuda) panellAjuda.hidden = false;
    }

    function amagaAjuda() {
        if (panellAjuda) panellAjuda.hidden = true;
    }

    function ajudaOberta() {
        return !!panellAjuda && !panellAjuda.hidden;
    }

    // --- Cicle de vida ---------------------------------------------------

    let scrollDocument = 0;
    let imprimint = false;

    /** Activa el mode presentació conservant el document original. */
    function activa() {
        if (actiu) return;
        actiu = true;
        scrollDocument = window.scrollY || 0;
        originals = Array.from(contingut.childNodes);
        rotul = calculaRotul();
        mode = MODUS_CONFIG;

        body.classList.add('mode-presentacio');
        contingut.classList.add('presentacio-actiu');
        contingut.classList.toggle('presentacio-scroll', mode === 'scroll');

        creaUI();
        munta();

        // Reprén on es va deixar (o on diga el hash #presentar/N).
        vésA(Math.min(recuperaPosicio(), slides.length - 1), { suau: false });
    }

    /** Torna el document a l'estat original, node a node. */
    function desactiva() {
        if (!actiu) return;
        actiu = false;
        clearTimeout(temporitzadorMesura);
        clearTimeout(temporitzadorScroll);
        clearTimeout(temporitzadorGuardar);

        amagaAjuda();
        llevaUI();

        body.classList.remove('mode-presentacio');
        contingut.classList.remove('presentacio-actiu', 'presentacio-scroll');
        contingut.replaceChildren(...(originals || []));
        originals = null;
        slides = [];
        index = 0;
        escriuHash('#');
        window.scrollTo(0, scrollDocument);
    }

    /** Els camps de text no han de disparar les tecles de presentació. */
    function esCampDeText(element) {
        if (!element || !element.tagName) return false;
        const tag = element.tagName.toLowerCase();
        return (
            tag === 'input' ||
            tag === 'textarea' ||
            tag === 'select' ||
            element.isContentEditable
        );
    }

    // --- Teclat ----------------------------------------------------------

    document.addEventListener('keydown', (event) => {
        if (event.defaultPrevented) return;
        if (event.ctrlKey || event.metaKey || event.altKey) return;
        if (esCampDeText(event.target)) return;

        // Fora de la presentació només ens interessa com activar-la.
        if (!actiu) {
            if (event.key === 'p' || event.key === 'P' || event.key === 'F5') {
                event.preventDefault();
                activa();
            }
            return;
        }

        // Amb l'ajuda oberta, Esc o ? la tanquen i prou.
        if (ajudaOberta()) {
            if (event.key === 'Escape' || event.key === '?') {
                event.preventDefault();
                amagaAjuda();
            }
            return;
        }

        // Si el focus és en un botó del peu, Espai i Enter són seus.
        const enPeu =
            event.target.closest && event.target.closest('.presentacio-peu');
        if (enPeu && (event.key === ' ' || event.key === 'Enter')) return;

        switch (event.key) {
            case 'ArrowRight':
            case 'ArrowDown':
            case 'PageDown':
            case ' ':
            case 'Spacebar':
                event.preventDefault();
                seguent();
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
                event.preventDefault();
                anterior();
                break;
            case 'Home':
                event.preventDefault();
                vésA(0);
                break;
            case 'End':
                event.preventDefault();
                vésA(slides.length - 1);
                break;
            case 'm':
            case 'M':
                canviaMode();
                break;
            case 't':
            case 'T':
                canviaTema();
                break;
            case 'f':
            case 'F':
                pantallaCompleta();
                break;
            case '?':
                event.preventDefault();
                mostraAjuda();
                break;
            case 'Escape':
                if (document.fullscreenElement) {
                    document.exitFullscreen().catch(() => {});
                } else {
                    desactiva();
                }
                break;
            default:
                break;
        }
    });

    // --- Esdeveniments globals -------------------------------------------

    contingut.addEventListener('scroll', enScroll, { passive: true });

    window.addEventListener(
        'resize',
        () => {
            if (actiu) programaReMesura();
        },
        { passive: true }
    );

    // Les fonts (Inter, Fira Code) canvien les mètriques del text: si es
    // mesura abans d'hora, les diapositives es repartixen malament. Quan
    // acaben de carregar es torna a mesurar.
    const remesuraQuanEstiga = () => {
        if (actiu && mode === 'diapositives') programaReMesura();
    };
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(remesuraQuanEstiga).catch(() => {});
    }
    window.addEventListener('load', remesuraQuanEstiga);

    document.addEventListener('fullscreenchange', () => {
        if (actiu) programaReMesura();
    });

    // En imprimir, el document ha de tornar a ser el de sempre; en acabar es
    // recupera la presentació on era.
    window.addEventListener('beforeprint', () => {
        if (!actiu) return;
        imprimint = true;
        desactiva();
    });

    window.addEventListener('afterprint', () => {
        if (!imprimint) return;
        imprimint = false;
        activa();
    });

    const botoPresentar = document.getElementById('presentacio-toggle');
    if (botoPresentar) {
        botoPresentar.addEventListener('click', (event) => {
            event.preventDefault();
            activa();
        });
    }

    // --- Arrancada --------------------------------------------------------

    /**
     * Espera que mermaid haja dibuixat els diagrames abans de mesurar: si no,
     * les diapositives es repartirien amb una alçada que encara no és la
     * definitiva. Si mermaid no hi és (sense connexió), no s'espera.
     */
    function esperaDibuixos(accio) {
        if (typeof mermaid === 'undefined') {
            accio();
            return;
        }
        const pendents = Array.from(document.querySelectorAll('.mermaid'));
        if (!pendents.length) {
            accio();
            return;
        }
        let intents = 0;
        const comprova = () => {
            const llestos = pendents.every(
                (node) => node.querySelector('svg') || node.dataset.processed
            );
            intents += 1;
            if (llestos || intents > 40) {
                accio();
                return;
            }
            setTimeout(comprova, 100);
        };
        comprova();
    }

    // Enllaç directe: ...html#presentar o ...html#presentar/3
    if (/^#presentar(?:\/\d+)?$/.test(location.hash)) {
        esperaDibuixos(activa);
    }
})();


