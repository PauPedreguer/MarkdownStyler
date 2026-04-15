#!/usr/bin/env python3
"""
Markdown Exporter Pro - App amb interfície gràfica
IES Pere Maria Orts i Bosch
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime


class MarkdownExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 Markdown Exporter Pro")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configurar estil
        self.configurar_estil()
        
        # Variables
        self.arxiu_md = tk.StringVar()
        self.assignatura = tk.StringVar()
        self.professor = tk.StringVar()
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.logo_path = tk.StringVar()
        
        # Crear interfície
        self.crear_widgets()
        
        # Carregar CSS per defecte
        self.carregar_css_per_defecte()
    
    def configurar_estil(self):
        """Configurar estil modern"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.colors = {
            'primari': '#2563eb',
            'fons': '#f8fafc',
            'superficie': '#ffffff',
            'text': '#1e293b',
            'bord': '#e2e8f0',
            'exit': '#10b981',
            'error': '#ef4444'
        }
        
        # Configurar estils
        self.style.configure('TFrame', background=self.colors['fons'])
        self.style.configure('TLabel', background=self.colors['fons'], font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8)
        self.style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground=self.colors['primari'])
        self.style.configure('Subheader.TLabel', font=('Segoe UI', 12), foreground=self.colors['text'])
        
        # Botons personalitzats
        self.style.configure('Primari.TButton', background=self.colors['primari'], foreground='white')
        self.style.map('Primari.TButton', background=[('active', '#1d4ed8')])
        
        self.style.configure('Exit.TButton', background=self.colors['exit'], foreground='white')
        self.style.map('Exit.TButton', background=[('active', '#059669')])
    
    def crear_widgets(self):
        """Crear la interfície"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # === HEADER ===
        header = ttk.Label(main_frame, text="📄 Markdown Exporter Pro", style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))
        
        subheader = ttk.Label(main_frame, text="IES Pere Maria Orts i Bosch", style='Subheader.TLabel')
        subheader.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        # === PANEL ESQUERRA: Configuració ===
        left_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuració", padding="15")
        left_frame.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=(0, 15))
        left_frame.columnconfigure(1, weight=1)
        
        # Arxiu Markdown
        ttk.Label(left_frame, text="📄 Arxiu Markdown:").grid(row=0, column=0, sticky="w", pady=5)
        file_frame = ttk.Frame(left_frame)
        file_frame.grid(row=0, column=1, sticky="ew", pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.arxiu_md)
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttk.Button(file_frame, text="📂", width=3, command=self.seleccionar_arxiu).grid(row=0, column=1)
        
        # Logo
        ttk.Label(left_frame, text="🖼️ Logo (opcional):").grid(row=1, column=0, sticky="w", pady=5)
        logo_frame = ttk.Frame(left_frame)
        logo_frame.grid(row=1, column=1, sticky="ew", pady=5)
        logo_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(logo_frame, textvariable=self.logo_path).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(logo_frame, text="📂", width=3, command=self.seleccionar_logo).grid(row=0, column=1)
        
        # Assignatura
        ttk.Label(left_frame, text="📚 Assignatura:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(left_frame, textvariable=self.assignatura).grid(row=2, column=1, sticky="ew", pady=5)
        
        # Professor
        ttk.Label(left_frame, text="👤 Professor/a:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(left_frame, textvariable=self.professor).grid(row=3, column=1, sticky="ew", pady=5)
        
        # Data
        ttk.Label(left_frame, text="📅 Data:").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(left_frame, textvariable=self.data).grid(row=4, column=1, sticky="ew", pady=5)
        
        # Format d'exportació
        ttk.Label(left_frame, text="📋 Format:").grid(row=5, column=0, sticky="w", pady=10)
        
        self.format_var = tk.StringVar(value="html")
        formats_frame = ttk.Frame(left_frame)
        formats_frame.grid(row=5, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(formats_frame, text="🌐 HTML amb navegació", variable=self.format_var, value="html").pack(anchor="w")
        ttk.Radiobutton(formats_frame, text="📄 PDF", variable=self.format_var, value="pdf").pack(anchor="w")
        ttk.Radiobutton(formats_frame, text="📝 Tots dos", variable=self.format_var, value="tots").pack(anchor="w")
        
        # Botó exportar
        ttk.Button(left_frame, text="🚀 EXPORTAR", style='Primari.TButton', command=self.exportar).grid(row=6, column=0, columnspan=2, pady=20, sticky="ew")
        
        # Botó obrir carpeta
        ttk.Button(left_frame, text="📂 Obrir carpeta d'exportació", command=self.obrir_carpeta).grid(row=7, column=0, columnspan=2, sticky="ew")
        
        # === PANEL DRET: CSS ===
        css_frame = ttk.LabelFrame(main_frame, text="🎨 CSS Personalitzat", padding="10")
        css_frame.grid(row=2, column=1, sticky="nsew", pady=(0, 10))
        css_frame.columnconfigure(0, weight=1)
        css_frame.rowconfigure(0, weight=1)
        
        self.css_text = scrolledtext.ScrolledText(css_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.css_text.grid(row=0, column=0, sticky="nsew")
        
        css_buttons = ttk.Frame(css_frame)
        css_buttons.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(css_buttons, text="🔄 Restablir per defecte", command=self.carregar_css_per_defecte).pack(side="left", padx=5)
        ttk.Button(css_buttons, text="💾 Guardar com a plantilla", command=self.guardar_plantilla).pack(side="left", padx=5)
        ttk.Button(css_buttons, text="📂 Carregar plantilla", command=self.carregar_plantilla).pack(side="left", padx=5)
        
        # === PANEL INFERIOR: Previsualització ===
        preview_frame = ttk.LabelFrame(main_frame, text="👁️ Vista prèvia (Markdown)", padding="10")
        preview_frame.grid(row=3, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, state="disabled", font=('Consolas', 10))
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        
        # Botó actualitzar preview
        ttk.Button(preview_frame, text="🔄 Actualitzar vista prèvia", command=self.actualitzar_preview).grid(row=1, column=0, pady=(10, 0))
    
    def carregar_css_per_defecte(self):
        """Carregar CSS modern per defecte"""
        css_default = '''/* Estil Minimalista Modern */
:root {
    --color-primari: #2563eb;
    --color-fons: #f8fafc;
    --color-text: #1e293b;
    --font-principal: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', Consolas, monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-principal);
    line-height: 1.7;
    color: var(--color-text);
    background: var(--color-fons);
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px;
}

h1 {
    font-size: 2.5rem;
    color: var(--color-primari);
    border-bottom: 3px solid var(--color-primari);
    padding-bottom: 15px;
    margin-bottom: 30px;
}

h2 {
    font-size: 1.5rem;
    margin-top: 40px;
    color: var(--color-primari);
}

pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.9rem;
    margin: 20px 0;
}

code {
    font-family: var(--font-mono);
    background: #e2e8f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
}

pre code { background: transparent; padding: 0; }

blockquote {
    border-left: 4px solid var(--color-primari);
    background: #eff6ff;
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 0 8px 8px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th {
    background: var(--color-primari);
    color: white;
    padding: 12px;
    text-align: left;
}

td {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
}

tr:nth-child(even) { background: #f8fafc; }'''
        
        self.css_text.delete(1.0, tk.END)
        self.css_text.insert(1.0, css_default)
    
    def seleccionar_arxiu(self):
        """Seleccionar arxiu Markdown"""
        filename = filedialog.askopenfilename(
            title="Seleccionar arxiu Markdown",
            filetypes=[("Markdown", "*.md"), ("Tots", "*.*")]
        )
        if filename:
            self.arxiu_md.set(filename)
            self.carregar_preview(filename)
    
    def seleccionar_logo(self):
        """Seleccionar logo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar logo",
            filetypes=[("Imatges", "*.png *.jpg *.jpeg *.svg"), ("Tots", "*.*")]
        )
        if filename:
            self.logo_path.set(filename)
    
    def carregar_preview(self, filepath):
        """Carregar contingut a la vista prèvia"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contingut = f.read()
            
            self.preview_text.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, contingut)
            self.preview_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut llegir l'arxiu:\\n{e}")
    
    def actualitzar_preview(self):
        """Actualitzar vista prèvia"""
        if self.arxiu_md.get():
            self.carregar_preview(self.arxiu_md.get())
    
    def guardar_plantilla(self):
        """Guardar CSS com a plantilla"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".css",
            filetypes=[("CSS", "*.css")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.css_text.get(1.0, tk.END))
            messagebox.showinfo("Èxit", "Plantilla guardada correctament!")
    
    def carregar_plantilla(self):
        """Carregar plantilla CSS"""
        filename = filedialog.askopenfilename(
            title="Carregar plantilla CSS",
            filetypes=[("CSS", "*.css"), ("Tots", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.css_text.delete(1.0, tk.END)
                self.css_text.insert(1.0, f.read())
    
    def generar_html(self, md_path, output_path):
        """Generar HTML amb navegació"""
        css = self.css_text.get(1.0, tk.END)
        
        # Llegir markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Extreure títols per navegació
        seccions = re.findall(r'^## (.+)$', md_content, re.MULTILINE)
        nav_html = "<ul>"
        for i, sec in enumerate(seccions, 1):
            sec_id = re.sub(r'[^a-z0-9]+', '-', sec.lower()).strip('-')
            nav_html += f'<li><a href="#{sec_id}">{i}. {sec}</a></li>'
        nav_html += "</ul>"
        
        # Convertir markdown a HTML
        try:
            result = subprocess.run(
                ['pandoc', md_path, '-t', 'html'],
                capture_output=True,
                text=True,
                check=True
            )
            body_html = result.stdout
        except:
            # Fallback si no hi ha pandoc
            body_html = f"<pre>{md_content}</pre>"
        
        # Construir HTML complet
        logo_html = ""
        if self.logo_path.get() and os.path.exists(self.logo_path.get()):
            # Convertir a base64 o usar path
            logo_html = f'<img src="{self.logo_path.get()}" class="logo" alt="Logo">'
        else:
            # Logo per defecte (SVG)
            logo_html = '''<svg width="80" height="80" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="#2563eb"/>
                <text x="50" y="60" text-anchor="middle" fill="white" font-size="30" font-weight="bold">IES</text>
            </svg>'''
        
        html_complet = f'''<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <title>{self.assignatura.get() or "Document"}</title>
    <style>
{css}
        
        /* Layout amb sidebar */
        body {{
            display: flex;
            margin: 0;
            min-height: 100vh;
            max-width: none;
            padding: 0;
        }}
        
        .sidebar {{
            width: 280px;
            background: white;
            border-right: 1px solid #e2e8f0;
            padding: 30px 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        
        .logo-container {{
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #2563eb;
            margin-bottom: 20px;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            margin-bottom: 10px;
        }}
        
        .info-assignatura h2 {{
            font-size: 1.1rem;
            color: #2563eb;
            margin: 0 0 10px 0;
        }}
        
        .info-assignatura p {{
            font-size: 0.9rem;
            color: #64748b;
            margin: 5px 0;
        }}
        
        .nav-seccions {{
            margin-top: 30px;
        }}
        
        .nav-seccions h3 {{
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 10px;
        }}
        
        .nav-seccions ul {{
            list-style: none;
            padding: 0;
        }}
        
        .nav-seccions li {{
            margin-bottom: 5px;
        }}
        
        .nav-seccions a {{
            display: block;
            padding: 8px 12px;
            color: #1e293b;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
            border-left: 3px solid transparent;
        }}
        
        .nav-seccions a:hover,
        .nav-seccions a.actiu {{
            background: #eff6ff;
            color: #2563eb;
            border-left-color: #2563eb;
        }}
        
        .main-content {{
            margin-left: 280px;
            flex: 1;
            padding: 40px;
            max-width: 900px;
        }}
        
        @media print {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; }}
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo-container">
            {logo_html}
            <h1 style="font-size: 1rem; color: #2563eb; margin: 0;">Pere Maria Orts i Bosch</h1>
        </div>
        
        <div class="info-assignatura">
            <h2>{self.assignatura.get() or "Assignatura"}</h2>
            <p>👤 {self.professor.get() or "Professor"}</p>
            <p>📅 {self.data.get()}</p>
        </div>
        
        <div class="nav-seccions">
            <h3>Contingut</h3>
            {nav_html}
        </div>
    </nav>
    
    <main class="main-content">
        {body_html}
    </main>
    
    <script>
        // Afegir IDs als h2
        document.querySelectorAll('h2').forEach(function(h2) {{
            const text = h2.textContent;
            const id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
            h2.id = id;
        }});
        
        // Scroll spy
        window.addEventListener('scroll', function() {{
            const seccions = document.querySelectorAll('h2[id]');
            const links = document.querySelectorAll('.nav-seccions a');
            
            let actual = '';
            seccions.forEach(function(sec) {{
                if (sec.getBoundingClientRect().top <= 100) {{
                    actual = sec.id;
                }}
            }});
            
            links.forEach(function(link) {{
                link.classList.remove('actiu');
                if (link.getAttribute('href') === '#' + actual) {{
                    link.classList.add('actiu');
                }}
            }});
        }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_complet)
        
        return True
    
    def exportar(self):
        """Exportar segons format seleccionat"""
        # Validacions
        if not self.arxiu_md.get():
            messagebox.showerror("Error", "Selecciona un arxiu Markdown!")
            return
        
        if not os.path.exists(self.arxiu_md.get()):
            messagebox.showerror("Error", "L'arxiu no existeix!")
            return
        
        # Crear carpeta d'exportació
        export_dir = Path.home() / "MarkdownExports"
        export_dir.mkdir(exist_ok=True)
        
        md_path = self.arxiu_md.get()
        base_name = Path(md_path).stem
        format_sel = self.format_var.get()
        
        exitos = []
        
        try:
            if format_sel in ["html", "tots"]:
                output_html = export_dir / f"{base_name}.html"
                self.generar_html(md_path, output_html)
                exitos.append(f"🌐 HTML: {output_html}")
            
            if format_sel in ["pdf", "tots"]:
                output_pdf = export_dir / f"{base_name}.pdf"
                try:
                    subprocess.run([
                        'pandoc', md_path, '-o', str(output_pdf),
                        '--pdf-engine=xelatex',
                        f'--metadata=title:{self.assignatura.get()}',
                        f'--metadata=author:{self.professor.get()}',
                        f'--metadata=date:{self.data.get()}'
                    ], check=True)
                    exitos.append(f"📄 PDF: {output_pdf}")
                except subprocess.CalledProcessError:
                    messagebox.showwarning("Atenció", "No s'ha pogut generar el PDF. ¿Tens pandoc i texlive instal·lats?")
            
            # Missatge d'èxit
            msg = "✅ Exportació completada!\\n\\n" + "\\n".join(exitos)
            messagebox.showinfo("Èxit", msg)
            
            # Obrir carpeta
            self.obrir_carpeta(export_dir)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en l'exportació:\\n{e}")
    
    def obrir_carpeta(self, carpeta=None):
        """Obrir carpeta d'exportació"""
        if carpeta is None:
            carpeta = Path.home() / "MarkdownExports"
            carpeta.mkdir(exist_ok=True)
        
        try:
            subprocess.run(['xdg-open', str(carpeta)], check=True)
        except:
            try:
                subprocess.run(['nautilus', str(carpeta)])
            except:
                messagebox.showinfo("Info", f"Arxius exportats a:\\n{carpeta}")


def main():
    root = tk.Tk()
    app = MarkdownExporterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()