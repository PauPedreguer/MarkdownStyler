#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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

        # Archivo
        tk.Label(main, text="Archivo Markdown", font=self.font_titol, bg=self.colors['fons']).pack(anchor='w')
        self.arxiu_md = tk.StringVar()
        tk.Entry(main, textvariable=self.arxiu_md).pack(fill='x', pady=5)
        self.crear_boton(main, "Seleccionar", self.seleccionar_arxiu).pack(pady=5)

        # Metadata
        tk.Label(main, text="Asignatura", bg=self.colors['fons']).pack(anchor='w')
        self.assignatura = tk.StringVar()
        tk.Entry(main, textvariable=self.assignatura).pack(fill='x', pady=2)

        tk.Label(main, text="Profesor", bg=self.colors['fons']).pack(anchor='w')
        self.professor = tk.StringVar()
        tk.Entry(main, textvariable=self.professor).pack(fill='x', pady=2)

        tk.Label(main, text="Fecha", bg=self.colors['fons']).pack(anchor='w')
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(main, textvariable=self.data).pack(fill='x', pady=2)

        # Botón exportar
        self.crear_boton(main, "Exportar", self.exportar, primario=True).pack(pady=10)

    # ----------------------
    # FILES
    # ----------------------
    def seleccionar_arxiu(self):
        file = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if file:
            self.arxiu_md.set(file)

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
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        output_html = Path(output_dir) / (Path(md).stem + ".html")

        try:
            result = subprocess.run([
                'pandoc',
                md,
                '-t', 'html5',
                '--standalone',
                '--toc',
                '--highlight-style=zenburn',
                f'--metadata=title:{self.assignatura.get()}',
                f'--metadata=author:{self.professor.get()}',
                f'--metadata=date:{self.data.get()}'
            ], capture_output=True, text=True, check=True)

            html = result.stdout

            # IDs únicos
            headers = re.findall(r'<h2>(.*?)</h2>', html)
            for i, h in enumerate(headers):
                slug = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
                new_id = f"{i}-{slug}"
                html = html.replace(f"<h2>{h}</h2>", f'<h2 id="{new_id}">{h}</h2>')

            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html)

            self.root.after(0, lambda: messagebox.showinfo("OK", f"Exportado en:\n{output_html}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownStylerApp(root)
    root.mainloop()