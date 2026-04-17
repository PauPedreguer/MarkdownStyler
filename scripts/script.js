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

    // --- 2. TOC COLLAPSIBLE LOGIC ---
    const tocItems = document.querySelectorAll('.toc li');
    
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

    // --- 3. COPY CODE BUTTON LOGIC ---
    const copyIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
    const checkIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

    const codeBlocks = document.querySelectorAll('pre');
    
    codeBlocks.forEach(block => {
        const container = block.parentElement.classList.contains('sourceCode') 
            ? block.parentElement 
            : block;
            
        container.style.position = 'relative';
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.title = 'Copiar codi';
        copyBtn.innerHTML = copyIcon;
        
        container.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', () => {
            const code = block.querySelector('code') || block;
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
    });
});
