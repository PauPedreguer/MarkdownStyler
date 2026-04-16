import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
from core.processor import process
import json
from pathlib import Path


def load_institut():
    return json.loads(Path("config/institut.json").read_text(encoding="utf-8"))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Styler")

        self.md_path = tk.StringVar()
        self.style = tk.StringVar()
        self.assignatura = tk.StringVar()
        self.title = tk.StringVar()
        self.professor = tk.StringVar()
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        self.build_ui()

    def build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(frame, text="Markdown").pack(anchor="w")
        tk.Entry(frame, textvariable=self.md_path).pack(fill="x")
        tk.Button(frame, text="Seleccionar", command=self.select_md).pack()

        tk.Label(frame, text="Estil").pack(anchor="w")
        tk.OptionMenu(frame, self.style, *self.get_styles()).pack(fill="x")

        tk.Label(frame, text="Assignatura").pack(anchor="w")
        tk.Entry(frame, textvariable=self.assignatura).pack(fill="x")
        
        tk.Label(frame, text="Títol pràctica").pack(anchor="w")
        tk.Entry(frame, textvariable=self.title).pack(fill="x")

        tk.Label(frame, text="Professor").pack(anchor="w")
        tk.Entry(frame, textvariable=self.professor).pack(fill="x")

        tk.Label(frame, text="Data").pack(anchor="w")
        tk.Entry(frame, textvariable=self.data).pack(fill="x")

        tk.Button(frame, text="Exportar", command=self.export).pack(pady=10)


    def select_md(self):
        file = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if file:
            self.md_path.set(file)
    
    def get_styles(self):
        from pathlib import Path
        styles_dir = Path("styles")
        return [f.name for f in styles_dir.glob("*.css")]
        

    def export(self):
        if not self.md_path.get():
            messagebox.showerror("Error", "Selecciona un markdown")
            return

        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        threading.Thread(target=self._export_thread, args=(output_dir,)).start()

    def _export_thread(self, output_dir):
        import os
        from pathlib import Path

        md = self.md_path.get()
        base = Path(md).stem
        output = os.path.join(output_dir, f"{base}.html")


        try:
            config = load_institut()
            
            process(
                md_path=md,
                css_path = f"styles/{self.style.get()}",
                output_path=output,
                metadata={
                    **config,
                    "title": self.title.get(),
                    "assignatura": self.assignatura.get(),
                    "professor": self.professor.get(),
                    "data": self.data.get()
                }
            )

            self.root.after(0, lambda: messagebox.showinfo(
                "OK", f"HTML generat:\n{output}"
            ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))