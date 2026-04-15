#!/usr/bin/env python3
"""
Markdown Styler - App amb estil GNOME Modern
IES Pere Maria Orts i Bosch
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime


class MarkdownStylerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Styler")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Colors estil GNOME (Adwaita)
        self.colors = {
            'fons': '#fafafa',
            'fons_fosc': '#f6f5f4',
            'superficie': '#ffffff',
            'text': '#2e2e2e',
            'text_secundari': '#5e5e5e',
            'bord': '#d0d0d0',
            'accent': '#3584e4',
            'accent_hover': '#1c71d8',
            'exit': '#26a269',
            'warning': '#e5a50a',
            'error': '#e01b24'
        }
        
        self.configurar_estil()
        self.crear_widgets()
        self.carregar_css_per_defecte()
        
        # Centrar finestra
        self.centrar_finestra()
    
    def configurar_estil(self):
        """Configurar estil GNOME modern"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar fonts del sistema
        self.font_normal = ('Cantarell', 11)
        self.font_titol = ('Cantarell', 13, 'bold')
        self.font_header = ('Cantarell', 24, 'bold')
        self.font_mono = ('Source Code Pro', 10)
        
        # Fons general
        self.root.configure(bg=self.colors['fons'])
        
        # Frame
        self.style.configure('TFrame', background=self.colors['fons'])
        
        # Labels
        self.style.configure('TLabel', 
                           background=self.colors['fons'], 
                           foreground=self.colors['text'],
                           font=self.font_normal)
        
        self.style.configure('Header.TLabel',
                           font=self.font_header,
                           foreground=self.colors['text'])
        
        self.style.configure('Subheader.TLabel',
                           font=('Cantarell', 14),
                           foreground=self.colors['text_secundari'])
        
        # Botons estil GNOME
        self.style.configure('TButton',
                           font=self.font_normal,
                           padding=(16, 8),
                           background=self.colors['superficie'],
                           foreground=self.colors['text'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.map('TButton',
                      background=[('active', self.colors['fons_fosc']),
                                 ('pressed', self.colors['bord'])],
                      foreground=[('active', self.colors['text'])])
        
        # Botó primari (suggerit)
        self.style.configure('Primari.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           font=('Cantarell', 11, 'bold'))
        
        self.style.map('Primari.TButton',
                      background=[('active', self.colors['accent_hover']),
                                 ('pressed', self.colors['accent'])],
                      foreground=[('active', 'white')])
        
        # Botó perillós/destrucció
        self.style.configure('Perill.TButton',
                           background=self.colors['error'],
                           foreground='white')
        
        # Entry
        self.style.configure('TEntry',
                           font=self.font_normal,
                           padding=8,
                           fieldbackground=self.colors['superficie'])
        
        # LabelFrame
        self.style.configure('TLabelframe',
                           background=self.colors['fons'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('TLabelframe.Label',
                           background=self.colors['fons'],
                           font=self.font_titol,
                           foreground=self.colors['text'])
        
        # Radiobutton
        self.style.configure('TRadiobutton',
                           background=self.colors['fons'],
                           font=self.font_normal)
        
        # PanedWindow
        self.style.configure('TPanedwindow', background=self.colors['fons'])
    
    def centrar_finestra(self):
        """Centrar la finestra a la pantalla"""
        self.root.update_idletasks()
        width = 1400
        height = 900
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_widgets(self):
        """Crear interfície estil GNOME"""
        # Frame principal amb padding
        main_container = tk.Frame(self.root, bg=self.colors['fons'])
        main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['fons'])
        header_frame.pack(fill='x', pady=(0, 24))
        
        tk.Label(header_frame, 
                text="Markdown Styler",
                font=self.font_header,
                bg=self.colors['fons'],
                fg=self.colors['text']).pack(anchor='w')
        
        tk.Label(header_frame,
                text="Exporta els teus documents amb estil",
                font=('Cantarell', 12),
                bg=self.colors['fons'],
                fg=self.colors['text_secundari']).pack(anchor='w')
        
        # PanedWindow per dividir esquerra/dreta
        paned = ttk.PanedWindow(main_container, orient='horizontal')
        paned.pack(fill='both', expand=True)
        
        # === PANEL ESQUERRA ===
        left_frame = tk.Frame(paned, bg=self.colors['fons'], width=400)
        paned.add(left_frame, weight=0)
        
        # Secció: Arxiu
        self.crear_seccio_arxiu(left_frame)
        
        # Separador
        tk.Frame(left_frame, bg=self.colors['bord'], height=1).pack(fill='x', pady=16)
        
        # Secció: Metadades
        self.crear_seccio_metadades(left_frame)
        
        # Separador
        tk.Frame(left_frame, bg=self.colors['bord'], height=1).pack(fill='x', pady=16)
        
        # Secció: Format
        self.crear_seccio_format(left_frame)
        
        # Separador
        tk.Frame(left_frame, bg=self.colors['bord'], height=1).pack(fill='x', pady=16)
        
        # Botons d'acció
        self.crear_botons_accio(left_frame)
        
        # === PANEL DRETA ===
        right_frame = tk.Frame(paned, bg=self.colors['fons'])
        paned.add(right_frame, weight=1)
        
        # Notebook per pestanyes
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestanya CSS
        self.crear_pestanya_css()
        
        # Pestanya Vista prèvia
        self.crear_pestanya_preview()
    
    def crear_seccio_arxiu(self, parent):
        """Secció de selecció d'arxiu"""
        frame = tk.Frame(parent, bg=self.colors['fons'])
        frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(frame, 
                text="Arxiu Markdown",
                font=self.font_titol,
                bg=self.colors['fons'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))
        
        # Selector d'arxiu millorat
        file_frame = tk.Frame(frame, bg=self.colors['fons'])
        file_frame.pack(fill='x')
        
        self.arxiu_md = tk.StringVar()
        
        self.entry_file = tk.Entry(file_frame,
                                  textvariable=self.arxiu_md,
                                  font=self.font_normal,
                                  bg=self.colors['superficie'],
                                  fg=self.colors['text'],
                                  relief='solid',
                                  borderwidth=1,
                                  highlightthickness=1,
                                  highlightcolor=self.colors['accent'],
                                  highlightbackground=self.colors['bord'])
        self.entry_file.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.entry_file.bind('<Button-1>', self.on_entry_click)
        
        btn_select = tk.Button(file_frame,
                              text="Seleccionar...",
                              font=self.font_normal,
                              bg=self.colors['superficie'],
                              fg=self.colors['text'],
                              activebackground=self.colors['fons_fosc'],
                              activeforeground=self.colors['text'],
                              relief='solid',
                              borderwidth=1,
                              cursor='hand2',
                              command=self.seleccionar_arxiu)
        btn_select.pack(side='right')
        
        # Logo opcional
        tk.Label(frame,
                text="Logo (opcional)",
                font=self.font_titol,
                bg=self.colors['fons'],
                fg=self.colors['text']).pack(anchor='w', pady=(16, 8))
        
        logo_frame = tk.Frame(frame, bg=self.colors['fons'])
        logo_frame.pack(fill='x')
        
        self.logo_path = tk.StringVar()
        
        self.entry_logo = tk.Entry(logo_frame,
                                  textvariable=self.logo_path,
                                  font=self.font_normal,
                                  bg=self.colors['superficie'],
                                  fg=self.colors['text'],
                                  relief='solid',
                                  borderwidth=1,
                                  highlightthickness=1,
                                  highlightcolor=self.colors['accent'],
                                  highlightbackground=self.colors['bord'])
        self.entry_logo.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.entry_logo.bind('<Button-1>', self.on_logo_click)
        
        btn_logo = tk.Button(logo_frame,
                            text="Seleccionar...",
                            font=self.font_normal,
                            bg=self.colors['superficie'],
                            fg=self.colors['text'],
                            activebackground=self.colors['fons_fosc'],
                            relief='solid',
                            borderwidth=1,
                            cursor='hand2',
                            command=self.seleccionar_logo)
        btn_logo.pack(side='right')
    
    def crear_seccio_metadades(self, parent):
        """Secció de metadades"""
        frame = tk.Frame(parent, bg=self.colors['fons'])
        frame.pack(fill='x')
        
        tk.Label(frame,
                text="Informació del document",
                font=self.font_titol,
                bg=self.colors['fons'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))
        
        # Camps de formulari
        camps = [
            ("Assignatura", "assignatura"),
            ("Professor/a", "professor"),
            ("Data", "data")
        ]
        
        self.assignatura = tk.StringVar()
        self.professor = tk.StringVar()
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        self.vars = {
            "assignatura": self.assignatura,
            "professor": self.professor,
            "data": self.data
        }
        
        for i, (label, key) in enumerate(camps):
            tk.Label(frame,
                    text=label,
                    font=self.font_normal,
                    bg=self.colors['fons'],
                    fg=self.colors['text_secundari']).pack(anchor='w', pady=(8, 4))
            
            entry = tk.Entry(frame,
                           textvariable=self.vars[key],
                           font=self.font_normal,
                           bg=self.colors['superficie'],
                           fg=self.colors['text'],
                           relief='solid',
                           borderwidth=1,
                           highlightthickness=1,
                           highlightcolor=self.colors['accent'],
                           highlightbackground=self.colors['bord'])
            entry.pack(fill='x', pady=(0, 8))
    
    def crear_seccio_format(self, parent):
        """Secció de format d'exportació"""
        frame = tk.Frame(parent, bg=self.colors['fons'])
        frame.pack(fill='x')
        
        tk.Label(frame,
                text="Format d'exportació",
                font=self.font_titol,
                bg=self.colors['fons'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))
        
        self.format_var = tk.StringVar(value="html")
        
        formats = [
            ("html", "🌐  HTML amb navegació lateral", "Ideal per a visualitzar al navegador"),
            ("pdf", "📄  PDF", "Document per a imprimir o compartir"),
            ("tots", "📝  Tots dos formats", "Genera HTML i PDF simultàniament")
        ]
        
        for val, text, desc in formats:
            radio_frame = tk.Frame(frame, bg=self.colors['fons'])
            radio_frame.pack(fill='x', pady=4)
            
            radio = tk.Radiobutton(radio_frame,
                                  variable=self.format_var,
                                  value=val,
                                  bg=self.colors['fons'],
                                  activebackground=self.colors['fons'],
                                  selectcolor=self.colors['accent'],
                                  font=self.font_normal,
                                  cursor='hand2')
            radio.pack(side='left')
            
            text_frame = tk.Frame(radio_frame, bg=self.colors['fons'])
            text_frame.pack(side='left', padx=(8, 0))
            
            tk.Label(text_frame,
                    text=text,
                    font=self.font_normal,
                    bg=self.colors['fons'],
                    fg=self.colors['text']).pack(anchor='w')
            
            tk.Label(text_frame,
                    text=desc,
                    font=('Cantarell', 9),
                    bg=self.colors['fons'],
                    fg=self.colors['text_secundari']).pack(anchor='w')
    
    def crear_botons_accio(self, parent):
        """Botons d'acció principals"""
        frame = tk.Frame(parent, bg=self.colors['fons'])
        frame.pack(fill='x', pady=(8, 0))
        
        # Botó exportar (primari)
        btn_export = tk.Button(frame,
                              text="🚀  Exportar document",
                              font=('Cantarell', 12, 'bold'),
                              bg=self.colors['accent'],
                              fg='white',
                              activebackground=self.colors['accent_hover'],
                              activeforeground='white',
                              relief='flat',
                              borderwidth=0,
                              padx=24,
                              pady=12,
                              cursor='hand2',
                              command=self.exportar)
        btn_export.pack(fill='x', pady=(0, 8))
        
        # Botó obrir carpeta (secundari)
        btn_open = tk.Button(frame,
                            text="📂  Obrir carpeta d'exportació",
                            font=self.font_normal,
                            bg=self.colors['superficie'],
                            fg=self.colors['text'],
                            activebackground=self.colors['fons_fosc'],
                            activeforeground=self.colors['text'],
                            relief='solid',
                            borderwidth=1,
                            padx=16,
                            pady=8,
                            cursor='hand2',
                            command=self.obrir_carpeta)
        btn_open.pack(fill='x')
    
    def crear_pestanya_css(self):
        """Pestanya d'edició CSS"""
        css_frame = tk.Frame(self.notebook, bg=self.colors['fons'])
        self.notebook.add(css_frame, text="  🎨  Estil CSS  ")
        
        # Toolbar
        toolbar = tk.Frame(css_frame, bg=self.colors['fons'])
        toolbar.pack(fill='x', pady=(0, 8))
        
        btn_default = tk.Button(toolbar,
                               text="🔄  Restablir per defecte",
                               font=self.font_normal,
                               bg=self.colors['superficie'],
                               relief='solid',
                               borderwidth=1,
                               cursor='hand2',
                               command=self.carregar_css_per_defecte)
        btn_default.pack(side='left', padx=(0, 8))
        
        btn_save = tk.Button(toolbar,
                            text="💾  Guardar plantilla",
                            font=self.font_normal,
                            bg=self.colors['superficie'],
                            relief='solid',
                            borderwidth=1,
                            cursor='hand2',
                            command=self.guardar_plantilla)
        btn_save.pack(side='left', padx=(0, 8))
        
        btn_load = tk.Button(toolbar,
                            text="📂  Carregar plantilla",
                            font=self.font_normal,
                            bg=self.colors['superficie'],
                            relief='solid',
                            borderwidth=1,
                            cursor='hand2',
                            command=self.carregar_plantilla)
        btn_load.pack(side='left')
        
        # Editor CSS
        self.css_text = scrolledtext.ScrolledText(css_frame,
                                                  wrap=tk.WORD,
                                                  font=self.font_mono,
                                                  bg=self.colors['superficie'],
                                                  fg=self.colors['text'],
                                                  relief='solid',
                                                  borderwidth=1,
                                                  highlightthickness=1,
                                                  highlightcolor=self.colors['accent'],
                                                  highlightbackground=self.colors['bord'],
                                                  padx=12,
                                                  pady=12)
        self.css_text.pack(fill='both', expand=True)
    
    def crear_pestanya_preview(self):
        """Pestanya de vista prèvia"""
        preview_frame = tk.Frame(self.notebook, bg=self.colors['fons'])
        self.notebook.add(preview_frame, text="  👁️  Vista prèvia  ")
        
        # Toolbar
        toolbar = tk.Frame(preview_frame, bg=self.colors['fons'])
        toolbar.pack(fill='x', pady=(0, 8))
        
        btn_refresh = tk.Button(toolbar,
                               text="🔄  Actualitzar",
                               font=self.font_normal,
                               bg=self.colors['superficie'],
                               relief='solid',
                               borderwidth=1,
                               cursor='hand2',
                               command=self.actualitzar_preview)
        btn_refresh.pack(side='left')
        
        # Àrea de preview
        self.preview_text = scrolledtext.ScrolledText(preview_frame,
                                                      wrap=tk.WORD,
                                                      state="disabled",
                                                      font=self.font_mono,
                                                      bg=self.colors['superficie'],
                                                      fg=self.colors['text'],
                                                      relief='solid',
                                                      borderwidth=1,
                                                      padx=12,
                                                      pady=12)
        self.preview_text.pack(fill='both', expand=True)
    
    def on_entry_click(self, event):
        """Gestionar clic a l'entry d'arxiu"""
        # No fer res especial, només permetre edició
        pass
    
    def on_logo_click(self, event):
        """Gestionar clic a l'entry de logo"""
        pass
    
    def seleccionar_arxiu(self):
        """Diàleg de selecció d'arxiu millorat"""
        filename = filedialog.askopenfilename(
            title="Seleccionar arxiu Markdown",
            filetypes=[
                ("Markdown", "*.md"),
                ("Tots els arxius", "*.*")
            ],
            defaultextension=".md"
        )
        if filename:
            self.arxiu_md.set(filename)
            self.carregar_preview(filename)
            # Actualitzar títol si està buit
            if not self.assignatura.get():
                nom = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
                self.assignatura.set(nom)
    
    def seleccionar_logo(self):
        """Diàleg de selecció de logo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar logo",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("SVG", "*.svg"),
                ("Tots", "*.*")
            ]
        )
        if filename:
            self.logo_path.set(filename)
    
    def carregar_preview(self, filepath):
        """Carregar vista prèvia"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contingut = f.read()
            
            self.preview_text.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, contingut)
            self.preview_text.config(state="disabled")
            
            # Canviar a pestanya de preview
            self.notebook.select(1)
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut llegir l'arxiu:\n{e}")
    
    def actualitzar_preview(self):
        """Actualitzar vista prèvia"""
        if self.arxiu_md.get():
            self.carregar_preview(self.arxiu_md.get())
    
    def carregar_css_per_defecte(self):
        """CSS modern per defecte"""
        css = '''/* Estil GNOME Modern */
:root {
    --color-primari: #3584e4;
    --color-fons: #fafafa;
    --color-text: #2e2e2e;
    --font-principal: 'Cantarell', -apple-system, sans-serif;
    --font-mono: 'Source Code Pro', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-principal);
    line-height: 1.6;
    color: var(--color-text);
    background: var(--color-fons);
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
}

h1 {
    font-size: 2rem;
    color: var(--color-primari);
    border-bottom: 2px solid var(--color-primari);
    padding-bottom: 12px;
    margin-bottom: 24px;
}

h2 {
    font-size: 1.5rem;
    margin-top: 32px;
    color: var(--color-primari);
}

pre {
    background: #241f31;
    color: #f6f5f4;
    padding: 16px;
    border-radius: 12px;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.9rem;
    margin: 16px 0;
}

code {
    font-family: var(--font-mono);
    background: #deddda;
    padding: 2px 6px;
    border-radius: 6px;
    font-size: 0.9em;
}

pre code { background: transparent; padding: 0; }

blockquote {
    border-left: 4px solid var(--color-primari);
    background: #e6f0fc;
    padding: 16px 20px;
    margin: 16px 0;
    border-radius: 0 12px 12px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th {
    background: var(--color-primari);
    color: white;
    padding: 12px 16px;
    text-align: left;
}

td {
    padding: 12px 16px;
    border-bottom: 1px solid #deddda;
}

tr:nth-child(even) { background: #f6f5f4; }'''
        
        self.css_text.delete(1.0, tk.END)
        self.css_text.insert(1.0, css)
    
    def guardar_plantilla(self):
        """Guardar CSS com a plantilla"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".css",
            filetypes=[("CSS", "*.css")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.css_text.get(1.0, tk.END))
            messagebox.showinfo("Èxit", "Plantilla guardada correctament")
    
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
        """Generar HTML amb navegació millorada"""
        css = self.css_text.get(1.0, tk.END)
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Extreure seccions
        seccions = re.findall(r'^## (.+)$', md_content, re.MULTILINE)
        nav_html = "<ul>"
        for i, sec in enumerate(seccions, 1):
            sec_id = re.sub(r'[^a-z0-9]+', '-', sec.lower()).strip('-')
            nav_html += f'<li><a href="#{sec_id}" onclick="return scrollToSection(\'{sec_id}\')">{i}. {sec}</a></li>'
        nav_html += "</ul>"
        
        # Convertir markdown
        try:
            result = subprocess.run(
                ['pandoc', md_path, '-t', 'html'],
                capture_output=True,
                text=True,
                check=True
            )
            body_html = result.stdout
        except:
            body_html = f"<pre>{md_content}</pre>"
        
        # Logo
        logo_html = ""
        if self.logo_path.get() and os.path.exists(self.logo_path.get()):
            import base64
            ext = Path(self.logo_path.get()).suffix.lower()
            mime = "image/svg+xml" if ext == ".svg" else f"image/{ext[1:]}"
            with open(self.logo_path.get(), "rb") as img:
                b64 = base64.b64encode(img.read()).decode()
            logo_html = f'<img src="data:{mime};base64,{b64}" class="logo" alt="Logo">'
        else:
            logo_html = '''<svg width="64" height="64" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <rect width="100" height="100" rx="20" fill="#3584e4"/>
                <text x="50" y="65" text-anchor="middle" fill="white" font-size="40" font-weight="bold">IES</text>
            </svg>'''
        
        html_complet = f'''<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    background: #f6f5f4;
}}

.sidebar {{
    width: 300px;
    background: white;
    border-right: 1px solid #deddda;
    padding: 24px;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0,0,0,0.05);
}}

.logo-container {{
    text-align: center;
    padding-bottom: 20px;
    border-bottom: 2px solid #3584e4;
    margin-bottom: 20px;
}}

.logo {{
    width: 64px;
    height: 64px;
    margin-bottom: 12px;
}}

.info-assignatura h2 {{
    font-size: 1.1rem;
    color: #3584e4;
    margin: 0 0 8px 0;
    font-weight: 600;
}}

.info-assignatura p {{
    font-size: 0.9rem;
    color: #5e5e5e;
    margin: 4px 0;
}}

.nav-seccions {{
    margin-top: 24px;
}}

.nav-seccions h3 {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #5e5e5e;
    margin-bottom: 12px;
    font-weight: 600;
}}

.nav-seccions ul {{
    list-style: none;
    padding: 0;
    margin: 0;
}}

.nav-seccions li {{
    margin-bottom: 4px;
}}

.nav-seccions a {{
    display: block;
    padding: 10px 14px;
    color: #2e2e2e;
    text-decoration: none;
    border-radius: 10px;
    font-size: 0.95rem;
    border-left: 3px solid transparent;
    transition: all 0.2s ease;
    cursor: pointer;
}}

.nav-seccions a:hover,
.nav-seccions a.actiu {{
    background: #e6f0fc;
    color: #3584e4;
    border-left-color: #3584e4;
}}

.main-content {{
    margin-left: 300px;
    flex: 1;
    padding: 40px;
    max-width: 900px;
    background: #fafafa;
    min-height: 100vh;
}}

/* Smooth scroll */
html {{
    scroll-behavior: smooth;
}}

@media print {{
    .sidebar {{ display: none; }}
    .main-content {{ margin-left: 0; background: white; }}
}}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo-container">
            {logo_html}
            <h1 style="font-size: 0.95rem; color: #3584e4; margin: 0; font-weight: 600;">Pere Maria Orts i Bosch</h1>
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

    // Scroll suau a secció
    function scrollToSection(id) {{
        const element = document.getElementById(id);
        if (element) {{
            element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            history.pushState(null, null, '#' + id);
            updateActiveLink(id);
            return false;
        }}
        return true;
    }}

    // Actualitzar link actiu
    function updateActiveLink(activeId) {{
        const links = document.querySelectorAll('.nav-seccions a');
        links.forEach(function(link) {{
            link.classList.remove('actiu');
            const href = link.getAttribute('href');
            if (href === '#' + activeId) {{
                link.classList.add('actiu');
            }}
        }});
    }}

    // Scroll spy millorat - detecta últimes seccions
    function updateScrollSpy() {{
        const seccions = document.querySelectorAll('h2[id]');
        const links = document.querySelectorAll('.nav-seccions a');
        const scrollPos = window.scrollY + 150; // offset
        
        let current = '';
        const docHeight = document.documentElement.scrollHeight;
        const windowBottom = window.scrollY + window.innerHeight;
        
        // Comprovar si estem al final del document
        if (windowBottom >= docHeight - 50) {{
            // Estem al final, seleccionar última secció
            const lastSection = seccions[seccions.length - 1];
            if (lastSection) {{
                current = lastSection.id;
            }}
        }} else {{
            // Cercar secció visible
            for (let i = 0; i < seccions.length; i++) {{
                const sec = seccions[i];
                const nextSec = seccions[i + 1];
                const secTop = sec.offsetTop;
                const nextTop = nextSec ? nextSec.offsetTop : Infinity;
                
                if (scrollPos >= secTop && scrollPos < nextTop) {{
                    current = sec.id;
                    break;
                }}
            }}
        }}
        
        if (current) {{
            updateActiveLink(current);
        }}
    }}

    // Throttled scroll listener
    let ticking = false;
    window.addEventListener('scroll', function() {{
        if (!ticking) {{
            window.requestAnimationFrame(function() {{
                updateScrollSpy();
                ticking = false;
            }});
            ticking = true;
        }}
    }});

    // Gestionar hash inicial
    if (window.location.hash) {{
        const id = window.location.hash.substring(1);
        setTimeout(function() {{
            const element = document.getElementById(id);
            if (element) {{
                element.scrollIntoView();
                updateActiveLink(id);
            }}
        }}, 100);
    }}

    // Inicialitzar
    updateScrollSpy();
</script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_complet)
        
        return True
    
    def exportar(self):
        """Exportar document"""
        if not self.arxiu_md.get():
            messagebox.showerror("Error", "Selecciona un arxiu Markdown primer")
            return
        
        if not os.path.exists(self.arxiu_md.get()):
            messagebox.showerror("Error", "L'arxiu seleccionat no existeix")
            return
        
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
                    messagebox.showwarning("Atenció", 
                        "No s'ha pogut generar el PDF.\\n\\n" +
                        "Assegura't de tenir instal·lat:\\n" +
                        "sudo dnf install pandoc texlive-xetex")
            
            if exitos:
                msg = "✅ Exportació completada!\\n\\n" + "\\n".join(exitos)
                messagebox.showinfo("Èxit", msg)
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
    app = MarkdownStylerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()