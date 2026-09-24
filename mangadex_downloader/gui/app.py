import sys
import tkinter as tk
from tkinter import ttk

from gui.redirector import TextRedirector
from gui.steps.step1_search import SearchStep
from gui.steps.step2_volumes import VolumesStep
from gui.steps.step3_config import ConfigStep
from gui.steps.step4_progress import ProgressStep

STEP_TITLES = ["Buscar Serie", "Idioma y Tomos", "Configuración", "Descargar"]


class MangaWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MangaDex Downloader Wizard")
        self.root.geometry("900x680")

        self.current_step = 1
        self.selected_manga = None  # lo rellena SearchStep

        self._build_header()

        container = ttk.Frame(self.root, padding=15)
        container.pack(fill="both", expand=True)

        self.step_search = SearchStep(container, self)
        self.step_volumes = VolumesStep(container, self)
        self.step_config = ConfigStep(container, self)
        self.step_progress = ProgressStep(container, self)
        self._steps = {
            1: self.step_search,
            2: self.step_volumes,
            3: self.step_config,
            4: self.step_progress,
        }

        # Redirección dual de prints (terminal + GUI)
        sys.stdout = TextRedirector(self.step_progress.log_text)

        self.show_step(1)

    # ---------------------------------------------------------- utilidades
    def ui(self, fn, *args, **kwargs):
        """Ejecuta fn en el hilo de Tkinter (seguro para llamar desde workers)."""
        self.root.after(0, lambda: fn(*args, **kwargs))

    # ---------------------------------------------------------- cabecera
    def _build_header(self):
        header = ttk.Frame(self.root, padding=(10, 15))
        header.pack(fill="x")

        self.step_labels = []
        for num, text in enumerate(STEP_TITLES, start=1):
            lbl = tk.Label(
                header, text=f"  {num}  {text}  ",
                font=("Arial", 10, "bold"),
                bg="#e0e0e0", fg="#666666", relief="flat", bd=4,
            )
            lbl.pack(side="left", expand=True, fill="x", padx=4)
            self.step_labels.append(lbl)

    def _update_header(self):
        for idx, lbl in enumerate(self.step_labels, start=1):
            if idx == self.current_step:
                lbl.config(bg="#2563eb", fg="white")
            elif idx < self.current_step:
                lbl.config(bg="#10b981", fg="white")
            else:
                lbl.config(bg="#e0e0e0", fg="#666666")

    # ---------------------------------------------------------- navegación
    def show_step(self, step):
        self.current_step = step
        self._update_header()
        for frame in self._steps.values():
            frame.pack_forget()
        self._steps[step].pack(fill="both", expand=True)

    def go_to_volumes(self):
        self.show_step(2)
        self.step_volumes.load()

    def start_download(self):
        keys = self.step_volumes.get_selected_keys()
        if not keys:
            return

        cfg = self.step_config
        volumes = {k: self.step_volumes.volumes[k] for k in keys}

        self.show_step(4)
        self.step_progress.start(
            manga_title=self.selected_manga["title"],
            volumes=volumes,
            language=self.step_volumes.language_code(),
            output_dir=cfg.output_dir(),
            export_epub=cfg.export_epub(),
            export_pdf=cfg.export_pdf(),
        )
