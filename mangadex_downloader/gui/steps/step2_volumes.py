import threading
import tkinter as tk
from tkinter import ttk, messagebox

from core.api import get_chapters
from core.chapters import chapter_label, chapter_sort_key, group_by_volume
from core.config import LANGUAGES


class VolumesStep(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.chapters = []
        self.volumes = {}
        self._build()

    # ---------------------------------------------------------- UI
    def _build(self):
        self.lbl_title = ttk.Label(self, text="Paso 2: Idioma y Tomos", font=("Arial", 12, "bold"))
        self.lbl_title.pack(anchor="w", pady=(0, 10))

        self.lang_frame = ttk.Frame(self)
        self.lang_frame.pack(fill="x", pady=5)

        ttk.Label(self.lang_frame, text="Idioma de traducción:").pack(side="left", padx=(0, 5))
        self.combo_lang = ttk.Combobox(self.lang_frame, values=list(LANGUAGES.keys()), state="readonly")
        self.combo_lang.set("Español")
        self.combo_lang.pack(side="left", padx=5)

        self.btn_reload = ttk.Button(self.lang_frame, text="Cargar / Recargar Tomos", command=self.load)
        self.btn_reload.pack(side="left", padx=10)

        # Spinner de carga (se muestra justo debajo de la fila de idioma)
        self.loading_frame = ttk.Frame(self)
        ttk.Label(
            self.loading_frame, text="⏳ Cargando tomos y capítulos desde MangaDex...",
            font=("Arial", 9, "bold"), foreground="#2563eb",
        ).pack(side="left", padx=5)
        self.spinner = ttk.Progressbar(self.loading_frame, mode="indeterminate", length=220)
        self.spinner.pack(side="left", padx=5)

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, pady=10)

        frame_vols = ttk.LabelFrame(panes, text="Tomos Disponibles (Multi-selección)")
        self.list_vols = tk.Listbox(frame_vols, selectmode=tk.EXTENDED, font=("Arial", 10))
        self.list_vols.pack(fill="both", expand=True, padx=5, pady=5)
        self.list_vols.bind("<<ListboxSelect>>", self.on_volume_selected)

        frame_caps = ttk.LabelFrame(panes, text="Contenido del Tomo")
        self.list_caps = tk.Listbox(frame_caps, font=("Arial", 9))
        self.list_caps.pack(fill="both", expand=True, padx=5, pady=5)

        panes.add(frame_vols, weight=1)
        panes.add(frame_caps, weight=1)

        nav = ttk.Frame(self)
        nav.pack(fill="x", pady=10)

        self.btn_back = ttk.Button(nav, text="< Anterior", command=lambda: self.app.show_step(1))
        self.btn_back.pack(side="left")
        self.btn_next = ttk.Button(nav, text="Configuración >", state="disabled",
                                   command=lambda: self.app.show_step(3))
        self.btn_next.pack(side="right")

    # ---------------------------------------------------------- estado
    def language_code(self):
        return LANGUAGES[self.combo_lang.get()]

    def get_selected_keys(self):
        keys = list(self.volumes.keys())
        return [keys[i] for i in self.list_vols.curselection()]

    # ---------------------------------------------------------- carga
    def load(self):
        manga = self.app.selected_manga
        if not manga:
            return

        self.lbl_title.config(text=f"Serie seleccionada: {manga['title']}")
        self.list_vols.delete(0, tk.END)
        self.list_caps.delete(0, tk.END)
        self.btn_next.config(state="disabled")

        self.loading_frame.pack(fill="x", pady=5, after=self.lang_frame)
        self.spinner.start(10)
        for w in (self.btn_reload, self.btn_back):
            w.config(state="disabled")
        self.combo_lang.config(state="disabled")

        lang_code = self.language_code()

        def worker():
            try:
                chapters = get_chapters(manga["id"], lang_code)
                chapters.sort(key=chapter_sort_key)
                self.app.ui(self._show_volumes, chapters)
            except Exception as e:
                self.app.ui(messagebox.showerror, "Error", str(e))
            finally:
                self.app.ui(self._finish_loading)

        threading.Thread(target=worker, daemon=True).start()

    def _show_volumes(self, chapters):
        self.chapters = chapters
        self.volumes = group_by_volume(chapters)
        self.list_vols.delete(0, tk.END)
        for vol_name, caps in self.volumes.items():
            self.list_vols.insert(tk.END, f"Tomo {vol_name} ({len(caps)} caps)")

    def _finish_loading(self):
        self.spinner.stop()
        self.loading_frame.pack_forget()
        self.btn_reload.config(state="normal")
        self.btn_back.config(state="normal")
        self.combo_lang.config(state="readonly")

    def on_volume_selected(self, event):
        keys = self.get_selected_keys()
        self.list_caps.delete(0, tk.END)

        if not keys:
            self.btn_next.config(state="disabled")
            return

        self.btn_next.config(state="normal")
        for key in keys:
            for c in self.volumes[key]:
                self.list_caps.insert(tk.END, chapter_label(c))
