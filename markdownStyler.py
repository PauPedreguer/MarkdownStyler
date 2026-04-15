#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime
import threading


class MarkdownStylerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Styler")
        self.root.geometry("1400x900")

        self.colors = {
            'fons': '#fafafa',
            'superficie': '#ffffff',
            'text': '#2e2e2e',
            'text_secundari': '#5e5e5e',
            'accent': '#3584e4'
        }

        self.font_normal = ('Arial', 11)
        self.font_titol = ('Arial', 13, 'bold')

        self.crear_widgets()

    # ----------------------
    # HELPERS
    # ----------------------
    def crear_boton(self, parent, text, command, primario=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.font_normal,
            bg=self.colors['accent'] if primario else self.colors['superficie'],
            fg='white' if primario else self.colors['text'],
            relief='flat' if primario else 'solid',
            cursor='hand2'
        )

    def comprobar_pandoc(self):
        try:
            subprocess.run(['pandoc', '--version'], capture_output=True)
            return True
        except:
            return False

    # ----------------------
    # UI
    # ----------------------
    def crear_widgets(self):
        main = tk.Frame(self.root, bg=self.colors['fons'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main, text="Archivo Markdown", font=self.font_titol, bg=self.colors['fons']).pack(anchor='w')
        self.arxiu_md = tk.StringVar()
        tk.Entry(main, textvariable=self.arxiu_md).pack(fill='x', pady=5)
        self.crear_boton(main, "Seleccionar", self.seleccionar_arxiu).pack(pady=5)

        # CSS
        tk.Label(main, text="Estilo (CSS)", bg=self.colors['fons']).pack(anchor='w')
        self.css_path = tk.StringVar()
        tk.Entry(main, textvariable=self.css_path).pack(fill='x', pady=2)
        self.crear_boton(main, "Seleccionar CSS", self.seleccionar_css).pack(pady=5)

        tk.Label(main, text="Asignatura", bg=self.colors['fons']).pack(anchor='w')
        self.assignatura = tk.StringVar()
        tk.Entry(main, textvariable=self.assignatura).pack(fill='x', pady=2)

        tk.Label(main, text="Profesor", bg=self.colors['fons']).pack(anchor='w')
        self.professor = tk.StringVar()
        tk.Entry(main, textvariable=self.professor).pack(fill='x', pady=2)

        tk.Label(main, text="Fecha", bg=self.colors['fons']).pack(anchor='w')
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(main, textvariable=self.data).pack(fill='x', pady=2)

        self.crear_boton(main, "Exportar", self.exportar, primario=True).pack(pady=10)

    # ----------------------
    # FILES
    # ----------------------
    def seleccionar_arxiu(self):
        file = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if file:
            name = Path(file).name
            if name.startswith('.') or name in ['.DS_Store', 'Thumbs.db']:
                messagebox.showwarning("Archivo no válido", "Archivo oculto o basura")
                return
            self.arxiu_md.set(file)
    def seleccionar_css(self):
        file = filedialog.askopenfilename(filetypes=[("CSS", "*.css")])
        if file:
            self.css_path.set(file)

    # ----------------------
    # EXPORT
    # ----------------------
    def exportar(self):
        if not self.arxiu_md.get():
            messagebox.showerror("Error", "Selecciona un archivo")
            return

        if not self.comprobar_pandoc():
            messagebox.showerror("Error", "Pandoc no está instalado")
            return

        threading.Thread(target=self._exportar_thread).start()

    def _exportar_thread(self):
        md = self.arxiu_md.get()

        # selector carpeta (en hilo principal para evitar problemas)
        output_dir = self.root.after(0, lambda: None)
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        base = Path(md).stem
        output_html = Path(output_dir) / f"{base}.html"
        output_pdf = Path(output_dir) / f"{base}.pdf"

        try:
            # HTML
            result = subprocess.run([
                'pandoc', md,
                '-t', 'html5',
                '--standalone',
                '--toc',
                '--highlight-style=zenburn',
                f'--metadata=title:{self.assignatura.get()}',
                f'--metadata=author:{self.professor.get()}',
                f'--metadata=date:{self.data.get()}'
            ], capture_output=True, text=True, check=True)

            html = result.stdout

            css_content = ""

            if self.css_path.get() and os.path.exists(self.css_path.get()):
                try:
                    with open(self.css_path.get(), 'r', encoding='utf-8') as f:
                        css_content = f.read()
                except:
                    css_content = ""

            # Inyectar CSS en el HTML
            if css_content:
                html = html.replace(
                    "</head>",
                    f"<style>\n{css_content}\n</style>\n</head>"
                )

            headers = re.findall(r'<h2>(.*?)</h2>', html)
            for i, h in enumerate(headers):
                slug = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
                html = html.replace(f"<h2>{h}</h2>", f'<h2 id="{i}-{slug}">{h}</h2>')

            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html)

            # PDF
            try:
                subprocess.run([
                    'pandoc', md,
                    '-o', str(output_pdf),
                    '--pdf-engine=xelatex',
                    f'--metadata=title:{self.assignatura.get()}',
                    f'--metadata=author:{self.professor.get()}',
                    f'--metadata=date:{self.data.get()}'
                ], check=True)
                pdf_msg = f"\nPDF: {output_pdf}"
            except:
                pdf_msg = "\n⚠️ PDF no generado (falta xelatex)"

            self.root.after(0, lambda: messagebox.showinfo(
                "OK",
                f"HTML: {output_html}{pdf_msg}"
            ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownStylerApp(root)
    root.mainloop()
