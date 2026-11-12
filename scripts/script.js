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

    const allPreBlocks = document.querySelectorAll('pre');

    allPreBlocks.forEach(pre => {
        const code = pre.querySelector('code');
        if (!code) return;

        // 3a. Detect Language
        const classes = Array.from(code.classList);
        const lang = classes.find(c => c !== 'sourceCode' && !c.startsWith('language-'));

        // Netejar els spans de numeració de línies de Pandoc.
        // Pandoc genera: <span id="cbN-M"><a ...></a>contingut</span>
        // Desempaquem els spans i enllaços però CONSERVEM el text tal qual,
        // perquè si el codi és HTML no es trenqui (no fem servir innerText/innerHTML).
        if (code.children.length > 0) {
            // Recórrer tots els nodes fills i substituir els spans per el seu text
            const walker = document.createTreeWalker(code, NodeFilter.SHOW_ELEMENT, {
                acceptNode(node) {
                    return (node.tagName === 'SPAN' || node.tagName === 'A')
                        ? NodeFilter.FILTER_ACCEPT
                        : NodeFilter.FILTER_SKIP;
                }
            });
            const toReplace = [];
            while (walker.nextNode()) {
                toReplace.push(walker.currentNode);
            }
            toReplace.forEach(el => {
                // Substituir l'element pel seu text (conserva el contingut com a text)
                el.replaceWith(document.createTextNode(el.textContent));
            });
        }

        if (lang) {
            code.classList.add(`language-${lang}`);
            pre.setAttribute('data-lang', lang);
            if (pre.parentElement.classList.contains('sourceCode')) {
                pre.parentElement.setAttribute('data-lang', lang);
            }
        }


        // 3b. Determinar el contenidor del bloc de codi
        const container = pre.parentElement.classList.contains('sourceCode')
            ? pre.parentElement
            : pre;

        // Evitar duplicats si es crida més d'un cop
        if (container.querySelector('.code-header')) return;

        // 3c. Crear la barra de capçalera amb el nom del llenguatge
        const header = document.createElement('div');
        header.className = 'code-header';

        const langLabel = document.createElement('span');
        langLabel.className = 'code-lang';
        langLabel.textContent = lang || 'text';

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
    // Ja no es carrega highlight.js (121 KB) ni cap postprocessat de tokens.
});
