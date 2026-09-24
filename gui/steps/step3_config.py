import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog

from core.config import DEFAULT_OUTPUT_DIR


class ConfigStep(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.var_output_dir = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))
        self.var_epub = tk.BooleanVar(value=True)
        self.var_pdf = tk.BooleanVar(value=True)
        self._build()

    # ---------------------------------------------------------- accesores
    def output_dir(self):
        return Path(self.var_output_dir.get().strip())

    def export_epub(self):
        return self.var_epub.get()

    def export_pdf(self):
        return self.var_pdf.get()

    # ---------------------------------------------------------- UI
    def _build(self):
        ttk.Label(self, text="Paso 3: Configuración de Exportación", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 15))

        group_path = ttk.LabelFrame(self, text=" Ruta de Guardado ", padding=12)
        group_path.pack(fill="x", pady=10)
        ttk.Label(group_path, text="Selecciona la carpeta en tu PC donde se guardarán los tomos:").pack(anchor="w", pady=(0, 5))

        path_box = ttk.Frame(group_path)
        path_box.pack(fill="x", pady=5)
        ttk.Entry(path_box, textvariable=self.var_output_dir, font=("Arial", 9)).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(path_box, text="Examinar...", command=self._browse).pack(side="left")

        group_fmt = ttk.LabelFrame(self, text=" Formatos a Exportar ", padding=12)
        group_fmt.pack(fill="x", pady=10)
        ttk.Label(group_fmt, text="Elige uno o ambos formatos para generar los tomos descargados:").pack(anchor="w", pady=(0, 8))
        ttk.Checkbutton(group_fmt, text="Generar archivo EPUB (.epub)", variable=self.var_epub).pack(anchor="w", pady=4)
        ttk.Checkbutton(group_fmt, text="Generar archivo PDF (.pdf)", variable=self.var_pdf).pack(anchor="w", pady=4)

        nav = ttk.Frame(self)
        nav.pack(fill="x", pady=(20, 0))
        ttk.Button(nav, text="< Anterior", command=lambda: self.app.show_step(2)).pack(side="left")
        ttk.Button(nav, text="Iniciar Descarga >", command=self._validate_and_start).pack(side="right")

    def _browse(self):
        selected = filedialog.askdirectory(initialdir=self.var_output_dir.get())
        if selected:
            self.var_output_dir.set(selected)

    def _validate_and_start(self):
        if not self.var_output_dir.get().strip():
            messagebox.showerror("Error de Configuración", "Por favor, selecciona una ruta de salida válida.")
            return

        if not self.export_epub() and not self.export_pdf():
            messagebox.showerror("Error de Configuración", "Debes seleccionar al menos un formato de exportación (EPUB o PDF).")
            return

        try:
            self.output_dir().mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error en Ruta", f"No se pudo crear o acceder a la carpeta especificada:\n{e}")
            return

        self.app.start_download()
