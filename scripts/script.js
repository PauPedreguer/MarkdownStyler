document.addEventListener('DOMContentLoaded', () => {

    // --- 0. DYNAMIC HEADER HEIGHT SYNC ---
    // Mesura l'alçada real del header i actualitza la variable CSS
    // perquè la sidebar i els ancoratges s'ajusten exactament.
    function syncHeaderHeight() {
        const header = document.querySelector('.header');
        if (header) {
            const h = header.getBoundingClientRect().height;
            document.documentElement.style.setProperty('--header-height', h + 'px');
        }
    }
    syncHeaderHeight();
    window.addEventListener('resize', syncHeaderHeight);

    // --- 0b. HEADER TOGGLE LOGIC ---
    // Permet amagar/mostrar la capçalera superior (com la barra lateral).
    const headerToggle = document.getElementById('header-toggle');
    if (headerToggle) {
        // Icones: fletxa cap amunt (amagar) / fletxa cap avall (mostrar)
        const chevronUp = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>';
        const chevronDown = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';

        function updateHeaderIcon() {
            const isCollapsed = document.body.classList.contains('header-collapsed');
            headerToggle.innerHTML = isCollapsed ? chevronDown : chevronUp;
            headerToggle.title = isCollapsed ? 'Mostrar capçalera' : 'Amagar capçalera';
        }

        headerToggle.addEventListener('click', () => {
            document.body.classList.toggle('header-collapsed');

            // Desa l'estat en localStorage per a la següent vegada
            const isCollapsed = document.body.classList.contains('header-collapsed');
            localStorage.setItem('header-collapsed', isCollapsed);

            // Actualitzar la icona i recalcular l'alçada de la capçalera
            updateHeaderIcon();
            syncHeaderHeight();
        });

        // Recuperar l'estat desat
        if (localStorage.getItem('header-collapsed') === 'true') {
            document.body.classList.add('header-collapsed');
        }
        updateHeaderIcon();
    }

    // --- 0c. FULLSCREEN TOGGLE LOGIC ---
    // Activa el mode pantalla completa del navegador i amaga la capçalera.
    const fullscreenToggle = document.getElementById('fullscreen-toggle');
    if (fullscreenToggle) {
        fullscreenToggle.addEventListener('click', () => {
            // Amagar la capçalera
            document.body.classList.add('header-collapsed');
            localStorage.setItem('header-collapsed', 'true');
            syncHeaderHeight();

            // Actualitzar la icona del botó de capçalera
            const headerToggle = document.getElementById('header-toggle');
            if (headerToggle) {
                headerToggle.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';
                headerToggle.title = 'Mostrar capçalera';
            }

            // Activar pantalla completa
            const el = document.documentElement;
            if (!document.fullscreenElement) {
                if (el.requestFullscreen) {
                    el.requestFullscreen();
                } else if (el.webkitRequestFullscreen) {
                    el.webkitRequestFullscreen();
                } else if (el.msRequestFullscreen) {
                    el.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
            }
        });
    }


    // --- 0d. TEMA CLAR / FOSC (una sola paleta per a tot el document) ---
    // La paleta viu a styles/base.css (html.tema-fosc) i el mode presentació
    // la reutilitza: no té tema propi. La preferència es desa i s'aplica
    // també abans del primer pintat des d'un script del <head>.
    const CLAU_TEMA = 'markdownstyler-tema';
    const ARREL = document.documentElement;
    const botoTema = document.getElementById('tema-toggle');

    const ICONA_LLUNA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    const ICONA_SOL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';

    function temaEsFosc() {
        return ARREL.classList.contains('tema-fosc');
    }

    function actualitzaBotoTema() {
        if (!botoTema) return;
        const fosc = temaEsFosc();
        botoTema.innerHTML = fosc ? ICONA_SOL : ICONA_LLUNA;
        botoTema.title = fosc ? 'Tema clar (T)' : 'Tema fosc (T)';
    }

    /**
     * API compartida amb scripts/presentacio.js (tecla T, botó del peu).
     * Treballa sempre sobre <html> perquè el tema no depén del mode.
     */
    const MSTema = {
        CLAU: CLAU_TEMA,

        /** Tema que s'està veient ara: 'clar' o 'fosc'. */
        actual() {
            return temaEsFosc() ? 'fosc' : 'clar';
        },

        /** Preferència desada per l'usuari ('clar' si encara no n'hi ha). */
        preferencia() {
            try {
                return localStorage.getItem(CLAU_TEMA) === 'fosc' ? 'fosc' : 'clar';
            } catch (error) {
                return 'clar';
            }
        },

        /** Aplica un tema sense desar-lo. Retorna el tema aplicat. */
        aplica(tema) {
            const fosc = tema === 'fosc';
            ARREL.classList.toggle('tema-fosc', fosc);
            actualitzaBotoTema();
            document.dispatchEvent(new CustomEvent('mstema-canvi', {
                detail: { tema: fosc ? 'fosc' : 'clar' }
            }));
            return fosc ? 'fosc' : 'clar';
        },

        /** Aplica la preferència desada; si no n'hi ha, `perDefecte`. */
        aplicaPreferencia(perDefecte = 'clar') {
            let desat = null;
            try {
                desat = localStorage.getItem(CLAU_TEMA);
            } catch (error) {
                desat = null;
            }
            if (desat === 'clar' || desat === 'fosc') return MSTema.aplica(desat);
            return MSTema.aplica(perDefecte === 'fosc' ? 'fosc' : 'clar');
        },

        /** Alterna el tema i el desa per a la pròxima vegada. */
        alterna() {
            const nou = temaEsFosc() ? 'clar' : 'fosc';
            try {
                localStorage.setItem(CLAU_TEMA, nou);
            } catch (error) {
                // Sense persistència (file:// privat, mode incògnit…): canvia igualment.
            }
            return MSTema.aplica(nou);
        }
    };
    window.MSTema = MSTema;

    // Arrancada: tema desat o, si és el primer colp, el que indique la
    // configuració (data-presentacio-tema). Per defecte, clar.
    MSTema.aplicaPreferencia(document.body.dataset.presentacioTema || 'clar');
    actualitzaBotoTema();

    if (botoTema) {
        botoTema.addEventListener('click', () => MSTema.alterna());
    }

    // Tecla T també fora de la presentació. Dins, la captura presentacio.js
    // (que crida a la mateixa API): així no es canvia dos voltes.
    document.addEventListener('keydown', (event) => {
        if (event.key !== 't' && event.key !== 'T') return;
        if (event.ctrlKey || event.metaKey || event.altKey) return;
        if (document.body.classList.contains('mode-presentacio')) return;
        const desti = event.target;
        if (desti && (desti.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(desti.tagName))) return;
        event.preventDefault();
        MSTema.alterna();
    });


    // --- 1. SIDEBAR TOGGLE LOGIC ---

    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-collapsed');
            
            // Desa l'estat en localStorage per a la següent vegada
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        });
        
        // Recuperar l'estat desat
        if (localStorage.getItem('sidebar-collapsed') === 'true') {
            document.body.classList.add('sidebar-collapsed');
        }
    }


    // --- 1b. CÒPIA DEL SUMARI PER A LA IMPRESSIÓ ---
    // Pandoc genera el $toc$ una sola vegada (a la barra lateral). La còpia
    // que s'imprimeix (.pdf-toc) es clona ací traient-li els ids per a no
    // duplicar identificadors al DOM (ids repetits = HTML invàlid i enllaços
    // ambigus). Es fa abans d'afegir els desplegables perquè la còpia surta
    // neta, sense les fletxetes ▾/▸.
    const sidebarToc = document.querySelector('.sidebar .toc');
    const printToc = document.querySelector('.pdf-toc .toc');
    if (sidebarToc && printToc) {
        const tocClone = sidebarToc.cloneNode(true);
        tocClone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
        printToc.replaceChildren(...Array.from(tocClone.childNodes));
    }


    // --- 2. TOC COLLAPSIBLE LOGIC ---
    // Només el sumari de la barra lateral és interactiu (el d'impressió és
    // una còpia estàtica).
    const tocItems = document.querySelectorAll('.sidebar .toc li');
    
    tocItems.forEach(item => {
        const subList = item.querySelector('ul');
        if (subList) {
            const toggle = document.createElement('span');
            toggle.className = 'toc-toggle';
            toggle.innerHTML = '▾';
            
            item.insertBefore(toggle, item.firstChild);
            
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                item.classList.toggle('is-collapsed');
                toggle.innerHTML = item.classList.contains('is-collapsed') ? '▸' : '▾';
            });
        }
    });

    // --- 3. CODE BLOCK ENHANCEMENTS (Header Bar, Copy Button) ---
    const copyIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
    const checkIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

    // Pandoc renombra alguns llenguatges (`c#` -> `cs`, `c++` -> `cpp`) i la
    // classe que emet no és per a llegir. Este mapa dóna el nom "humà" que es
    // mostra a la barra del bloc de codi.
    const ETIQUETES_LLENGUATGE = {
        cs: 'C#',
        cpp: 'C++',
        js: 'JavaScript',
        javascript: 'JavaScript',
        ts: 'TypeScript',
        typescript: 'TypeScript',
        bash: 'Bash',
        sh: 'Bash',
        py: 'Python',
        python: 'Python',
        html: 'HTML',
        css: 'CSS',
        php: 'PHP',
        sql: 'SQL',
    };

    // Classes que pandoc posa al <pre> i que NO són el nom d'un llenguatge (les
    // afig quan el bloc no es pot ressaltar o quan demana números de línia).
    const CLASSES_DE_PANDOC = new Set([
        'sourceCode', 'numberLines', 'numberSource', 'lineAnchors', 'example',
    ]);

    // --- 2b. RESSALTAT DE CRIDES ---
    // Pandoc (skylighting) treballa amb expressions regulars i no sap què és
    // una crida: en Kotlin, Java, JavaScript… un identificador seguit de
    // parèntesis (`Column(`, `Modifier.fillMaxSize(`, `println(`) queda sense
    // color. En codi de classe (i sobretot en Jetpack Compose) són justament
    // les paraules que més es miren, així que les marquem amb la classe `fu`
    // (Function) perquè agafen el color de funcions del tema de ressaltat.
    //
    // Només s'activa en llenguatges on `nom(` és una crida, i només sobre els
    // textos que NO estan dins d'un <span class="…"> de pandoc: els tokens que
    // pandoc ja ha pintat (paraules clau, tipus, cadenes…) no es toquen mai.
    const LLENGUATGES_AMB_CRIDES = new Set([
        'kotlin', 'java', 'javascript', 'typescript', 'cpp', 'cs', 'php',
        'python', 'py', 'js', 'ts',
    ]);

    // Paraules que van seguides de parèntesis però no són crides.
    const NO_SON_CRIDES = new Set([
        'if', 'for', 'while', 'switch', 'when', 'catch', 'return', 'new',
        'else', 'do', 'try', 'throw', 'finally', 'super', 'this', 'typeof',
        'sizeof', 'delete', 'await', 'yield', 'function', 'def', 'in', 'is',
        'as',
    ]);

    // Pandoc separa cada token en un <span>: `Column` i el parèntesi de
    // `Column(` són dos elements distints, així que no n'hi ha prou de mirar
    // dins del text: cal mirar el començament del següent germà.
    function seguentCaracter(node) {
        let germa = node.nextSibling;
        while (germa) {
            const text = (germa.textContent || '').trimStart();
            if (text) return text[0];
            germa = germa.nextSibling;
        }
        return '';
    }

    function anteriorCaracter(node) {
        let germa = node.previousSibling;
        while (germa) {
            const text = (germa.textContent || '').trimEnd();
            if (text) return text[text.length - 1];
            germa = germa.previousSibling;
        }
        return '';
    }

    function esCrida(text, index, llarg, node) {
        const resta = text.slice(index + llarg).trimStart();
        if (resta) return resta[0] === '(';
        return seguentCaracter(node) === '(';
    }

    // Un nom de tipus (`Modifier`, `Arrangement`, `Persona`…) comença amb
    // majúscula i té alguna minúscula. S'exclouen les constants (`MAX_SIZE`)
    // i l'accés a un membre (`Arrangement.Center`: `Center` és una propietat).
    function esTipus(nom, text, index, node) {
        if (!/^[A-Z]/.test(nom) || !/[a-z]/.test(nom)) return false;
        const abans = text.slice(0, index).trimEnd();
        const anterior = abans ? abans[abans.length - 1] : anteriorCaracter(node);
        return anterior !== '.';
    }

    function marcaCrides(code, lang) {
        if (!LLENGUATGES_AMB_CRIDES.has(lang)) return;

        const walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
        const textos = [];
        while (walker.nextNode()) textos.push(walker.currentNode);

        textos.forEach(node => {
            // Un token de pandoc: el text ja té color, no s'hi toca.
            if (node.parentElement.closest('span[class], a')) return;

            const text = node.nodeValue;
            // Un identificador que no ve precedit de paraula ni de `$`
            // (variables de Kotlin o de PHP).
            const re = /(?<![\w$])([A-Za-z_]\w*)/g;
            let fragment = null;
            let ultim = 0;
            let m;
            while ((m = re.exec(text)) !== null) {
                const classe = classePerIdentificador(m, text, node);
                if (!classe) continue;
                fragment = fragment || document.createDocumentFragment();
                if (m.index > ultim) {
                    fragment.appendChild(
                        document.createTextNode(text.slice(ultim, m.index))
                    );
                }
                const span = document.createElement('span');
                span.className = classe;
                span.textContent = m[1];
                fragment.appendChild(span);
                ultim = m.index + m[1].length;
            }
            if (!fragment) return;
            if (ultim < text.length) {
                fragment.appendChild(document.createTextNode(text.slice(ultim)));
            }
            // Es canvia només este text; els spans de pandoc queden intactes
            // perquè l'element <code> no es reconstrueix mai.
            node.replaceWith(fragment);
        });
    }

    // Classe de ressaltat que li toca a un identificador que pandoc ha deixat
    // sense color: `fu` si és una crida, `dt` si pareix un tipus, res si no.
    function classePerIdentificador(m, text, node) {
        if (NO_SON_CRIDES.has(m[1])) return null;
        if (esCrida(text, m.index, m[1].length, node)) return 'fu';
        if (esTipus(m[1], text, m.index, node)) return 'dt';
        return null;
    }

    const allPreBlocks = document.querySelectorAll('pre');

    allPreBlocks.forEach(pre => {
        const code = pre.querySelector('code');
        if (!code) return;

        // 3a. Detect Language
        const classes = Array.from(code.classList);
        let lang = classes.find(c => c !== 'sourceCode' && !c.startsWith('language-'));

        // Si pandoc no ressalta el bloc, la classe del llenguatge la posa al
        // <pre> (<pre class="text">, <pre class="foobar">). Així l'etiqueta diu
        // el que ha escrit l'usuari i no sempre "TEXT".
        if (!lang) {
            lang = Array.from(pre.classList).find(
                c => !CLASSES_DE_PANDOC.has(c) && !c.startsWith('language-')
            );
        }

        // IMPORTANT: no tocar els fills de <code>. Pandoc hi posa un
        // <span id="cbN-M"> per línia i, dins, un <span class="kw">,
        // <span class="st">… per token amb els colors de --highlight-style.
        // Ací abans es desempaquetaven eixos spans (perquè highlight.js
        // partira de zero), cosa que destruïa els tokens i deixava el bloc
        // sense ressaltat: tot el codi s'heretava del color del <pre>.

        if (lang) {
            code.classList.add(`language-${lang}`);
            pre.setAttribute('data-lang', lang);
        }

        // 3a-bis. Pintar les crides que pandoc no ha pogut reconéixer.
        marcaCrides(code, lang);


        // 3b. Determinar el contenidor del bloc de codi.
        // Pandoc només embolcalla en <div class="sourceCode"> els blocs que sap
        // ressaltar; la resta (``` sense info string, ```text, ```foobar)
        // arriben com a <pre> solt. Si la barra s'inserira dins del <pre>
        // quedaria dins del seu padding: sagnada respecte del bloc, més curta
        // que la seua vora i amb la tipografia del codi. Es crea el mateix
        // embolcall que fa pandoc perquè tots els blocs es vegen igual.
        let container = pre.parentElement.classList.contains('sourceCode')
            ? pre.parentElement
            : null;

        if (!container) {
            container = document.createElement('div');
            container.className = 'sourceCode';
            pre.replaceWith(container);
            container.appendChild(pre);
        }

        if (lang) container.setAttribute('data-lang', lang);

        // Evitar duplicats si es crida més d'un cop
        if (container.querySelector('.code-header')) return;

        // 3c. Crear la barra de capçalera amb el nom del llenguatge
        const header = document.createElement('div');
        header.className = 'code-header';

        const langLabel = document.createElement('span');
        langLabel.className = 'code-lang';
        langLabel.textContent = ETIQUETES_LLENGUATGE[lang] || lang || 'text';

        header.appendChild(langLabel);

        // 3d. Botó de copiar (dins la barra de capçalera)
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.title = 'Copiar codi';
        copyBtn.innerHTML = copyIcon;

        copyBtn.addEventListener('click', () => {
            const text = code.innerText;
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = checkIcon;
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = copyIcon;
                    copyBtn.classList.remove('copied');
                }, 2000);
            });
        });

        header.appendChild(copyBtn);

        // Inserir la barra al principi del contenidor
        container.insertBefore(header, container.firstChild);

    });

    // NOTA: el ressaltat de codi el fa Pandoc (--highlight-style) amb els
    // spans `code span.*` que injecta la plantilla via $highlighting-css$.
    // Ja no es carrega highlight.js (121 KB). L'únic afegit és `marcaCrides`,
    // que pinta les crides que pandoc no reconeix (Column(, println(…)).
});
