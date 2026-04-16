#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
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
        self.root.geometry("800x500")

        self.colors = {
            'fons': '#fafafa',
            'superficie': '#ffffff',
            'text': '#2e2e2e',
            'accent': '#3584e4'
        }

        self.font = ('Arial', 11)
        self.crear_widgets()

    # ----------------------
    # UI
    # ----------------------
    def crear_widgets(self):
        main = tk.Frame(self.root, bg=self.colors['fons'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        # Markdown
        tk.Label(main, text="Archivo Markdown", bg=self.colors['fons']).pack(anchor='w')
        self.arxiu_md = tk.StringVar()
        tk.Entry(main, textvariable=self.arxiu_md).pack(fill='x')
        tk.Button(main, text="Seleccionar", command=self.seleccionar_arxiu).pack(pady=5)

        # CSS
        tk.Label(main, text="CSS", bg=self.colors['fons']).pack(anchor='w')
        self.css_path = tk.StringVar()
        tk.Entry(main, textvariable=self.css_path).pack(fill='x')
        tk.Button(main, text="Seleccionar CSS", command=self.seleccionar_css).pack(pady=5)

        # Metadata
        tk.Label(main, text="Asignatura", bg=self.colors['fons']).pack(anchor='w')
        self.assignatura = tk.StringVar()
        tk.Entry(main, textvariable=self.assignatura).pack(fill='x')

        tk.Label(main, text="Profesor", bg=self.colors['fons']).pack(anchor='w')
        self.professor = tk.StringVar()
        tk.Entry(main, textvariable=self.professor).pack(fill='x')

        tk.Label(main, text="Fecha", bg=self.colors['fons']).pack(anchor='w')
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(main, textvariable=self.data).pack(fill='x')

        tk.Button(main, text="Exportar HTML", bg=self.colors['accent'], fg='white',
                  command=self.exportar).pack(pady=15)

    # ----------------------
    # FILES
    # ----------------------
    def seleccionar_arxiu(self):
        file = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if file:
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

        # 🔥 IMPORTANT: fora del thread
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        threading.Thread(target=self._exportar_thread, args=(output_dir,)).start()

    def _exportar_thread(self, output_dir):
        md = self.arxiu_md.get()
        base = Path(md).stem
        output_html = Path(output_dir) / f"{base}.html"

        try:
            # 1. Convertir markdown → HTML
            result = subprocess.run([
                'pandoc', md,
                '-t', 'html5',
                '--toc',
                '--highlight-style=zenburn'
                '--section-divs',
            ], capture_output=True, text=True, check=True)

            body_html = result.stdout

            # 2. IDs únics
            headers = re.findall(r'<h2>(.*?)</h2>', body_html)
            for i, h in enumerate(headers):
                slug = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
                body_html = body_html.replace(
                    f"<h2>{h}</h2>",
                    f'<h2 id="{i}-{slug}">{h}</h2>'
                )

            # 3. Navegació
            nav = "<ul>"
            for i, h in enumerate(headers):
                slug = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
                nav += f'<li><a href="#{i}-{slug}">{h}</a></li>'
            nav += "</ul>"

            # 4. CSS
            css_content = ""
            if self.css_path.get() and os.path.exists(self.css_path.get()):
                with open(self.css_path.get(), 'r', encoding='utf-8') as f:
                    css_content = f.read()

            # 5. Logo
            logo_html = '<div class="logo">IES</div>'

            # 6. Plantilla
            template_path = Path("templates/base.html")

            if not template_path.exists():
                raise Exception(f"No s'ha trobat la plantilla: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # 7. Reemplaçar variables
            html = template \
                .replace("{{title}}", self.assignatura.get()) \
                .replace("{{css}}", css_content) \
                .replace("{{assignatura}}", self.assignatura.get()) \
                .replace("{{professor}}", self.professor.get()) \
                .replace("{{data}}", self.data.get()) \
                .replace("{{nav}}", nav) \
                .replace("{{content}}", body_html) \
                .replace("{{logo}}", logo_html)

            # DEBUG
            print("Guardant en:", output_html)

            # 8. Guardar
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html)

            self.root.after(0, lambda: messagebox.showinfo(
                "OK",
                f"HTML generat en:\n{output_html}"
            ))

        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", str(e)))


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownStylerApp(root)
    root.mainloop()