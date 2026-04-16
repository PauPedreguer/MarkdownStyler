import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from pathlib import Path

from src.core.models import ExportOptions
from src.use_cases.generate_html import execute_export
from src.infrastructure.config_repo import load_institut_config, save_institut_config

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Styler (Clean)")
        self.root.geometry("450x450")
        
        self.md_path = tk.StringVar()
        self.style = tk.StringVar()
        self.title = tk.StringVar()
        self.data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        self.build_ui()

    def build_ui(self):
        # Tauler superior per ajustos
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill="x", padx=10, pady=5)
        tk.Button(toolbar, text="⚙️ Ajustos", command=self.open_settings).pack(side="right")

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(frame, text="Fitxer Markdown", font=("Arial", 9, "bold")).pack(anchor="w")
        
        file_frame = tk.Frame(frame)
        file_frame.pack(fill="x", pady=(0, 15))
        tk.Entry(file_frame, textvariable=self.md_path).pack(side="left", fill="x", expand=True)
        tk.Button(file_frame, text="Seleccionar", command=self.select_md).pack(side="right", padx=(5,0))

        tk.Label(frame, text="Estil CSS", font=("Arial", 9, "bold")).pack(anchor="w")
        styles = self.get_styles()
        if styles:
            self.style.set(styles[0])
            tk.OptionMenu(frame, self.style, *styles).pack(fill="x", pady=(0, 15))
        else:
            tk.Label(frame, text="(Cap estil trobat a styles/)").pack(anchor="w", pady=(0, 15))
        
        tk.Label(frame, text="Títol pràctica", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=self.title).pack(fill="x", pady=(0, 15))

        tk.Label(frame, text="Data", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=self.data).pack(fill="x", pady=(0, 25))

        tk.Button(frame, text="Exportar HTML", command=self.export, bg="#2563eb", fg="white", font=("Arial", 11, "bold"), pady=5).pack(fill="x")

    def select_md(self):
        file = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if file:
            self.md_path.set(file)
            # Autoemplenar el títol si està buit, posant el nom del fitxer
            if not self.title.get():
                self.title.set(Path(file).stem)
    
    def get_styles(self):
        styles_dir = Path("styles")
        if not styles_dir.exists():
            return []
        return sorted([f.name for f in styles_dir.glob("*.css")])

    def open_settings(self):
        top = tk.Toplevel(self.root)
        top.title("Ajustos de l'Institut")
        top.geometry("450x450")
        top.grab_set()

        config = load_institut_config()
        
        nom_var = tk.StringVar(value=config.get("institut_nom", ""))
        logo_var = tk.StringVar(value=config.get("institut_logo", ""))
        curs_var = tk.StringVar(value=config.get("curs", ""))
        assig_var = tk.StringVar(value=config.get("assignatura", ""))
        prof_var = tk.StringVar(value=config.get("professor", ""))

        frame = tk.Frame(top)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(frame, text="Nom de l'institut:", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=nom_var).pack(fill="x", pady=(0, 12))

        tk.Label(frame, text="Ruta del Logo:", font=("Arial", 9, "bold")).pack(anchor="w")
        logo_frame = tk.Frame(frame)
        logo_frame.pack(fill="x", pady=(0, 12))
        tk.Entry(logo_frame, textvariable=logo_var).pack(side="left", fill="x", expand=True)
        tk.Button(logo_frame, text="Cercar", command=lambda: logo_var.set(filedialog.askopenfilename(filetypes=[("Imatges", "*.png *.jpg *.jpeg *.svg")]))).pack(side="right", padx=(5,0))

        tk.Label(frame, text="Curs:", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=curs_var).pack(fill="x", pady=(0, 12))

        tk.Label(frame, text="Assignatura:", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=assig_var).pack(fill="x", pady=(0, 12))

        tk.Label(frame, text="Professor:", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Entry(frame, textvariable=prof_var).pack(fill="x", pady=(0, 20))

        def save():
            new_config = {
                "institut_nom": nom_var.get(),
                "institut_logo": logo_var.get(),
                "curs": curs_var.get(),
                "assignatura": assig_var.get(),
                "professor": prof_var.get()
            }
            save_institut_config(new_config)
            top.destroy()
            messagebox.showinfo("Guardat", "S'han desat els ajustos de manera persistent.")

        tk.Button(frame, text="Desar Ajustos", command=save, bg="#10b981", fg="white", font=("Arial", 10, "bold"), pady=4).pack(fill="x")

    def export(self):
        if not self.md_path.get():
            messagebox.showerror("Error", "Selecciona un markdown abans d'exportar.")
            return

        output_dir = filedialog.askdirectory(title="Selecciona la carpeta d'exportació")
        if not output_dir:
            return

        threading.Thread(target=self._export_thread, args=(output_dir,), daemon=True).start()

    def _export_thread(self, output_dir):
        md = self.md_path.get()
        base = Path(md).stem
        output = os.path.join(output_dir, f"{base}.html")
        
        css_path = ""
        if self.style.get():
            css_path = f"styles/{self.style.get()}"

        try:
            options = ExportOptions(
                md_path=md,
                output_path=output,
                css_path=css_path,
                title=self.title.get(),
                data=self.data.get()
            )
            
            execute_export(options)

            self.root.after(0, lambda: messagebox.showinfo(
                "OK", f"L'HTML s'ha generat correctament al següent repositori:\n{output}"
            ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error al Convertir", str(e)))
