import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from core.api import get_chapters
from core.chapters import chapter_label, chapter_sort_key, group_by_volume
from core.config import LANGUAGES


class VolumesStep(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.chapters = []
        self.volumes = {}
        self.custom_groups = []  # lista de (nombre, [capitulos])
        self.mode = tk.StringVar(value="tomos")
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

        # ---------------------------------------------------- selector de modo
        self.mode_frame = ttk.LabelFrame(self, text="Modo de descarga")
        self.mode_frame.pack(fill="x", pady=(5, 10))
        ttk.Radiobutton(
            self.mode_frame, text="Tomos establecidos (agrupados por MangaDex)",
            variable=self.mode, value="tomos", command=self._on_mode_change,
        ).pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(
            self.mode_frame, text="Selección personalizada de capítulos",
            variable=self.mode, value="personalizada", command=self._on_mode_change,
        ).pack(side="left", padx=10, pady=5)

        self.panes_container = ttk.Frame(self)
        self.panes_container.pack(fill="both", expand=True, pady=5)

        # ---------------------------------------------------- modo: tomos
        self.frame_tomos = ttk.Frame(self.panes_container)
        panes = ttk.PanedWindow(self.frame_tomos, orient="horizontal")
        panes.pack(fill="both", expand=True)

        frame_vols = ttk.LabelFrame(panes, text="Tomos Disponibles (Multi-selección)")
        self.list_vols = tk.Listbox(frame_vols, selectmode=tk.EXTENDED, font=("Arial", 10))
        self.list_vols.pack(fill="both", expand=True, padx=5, pady=5)
        self.list_vols.bind("<<ListboxSelect>>", self.on_volume_selected)

        frame_caps = ttk.LabelFrame(panes, text="Contenido del Tomo")
        self.list_caps = tk.Listbox(frame_caps, font=("Arial", 9))
        self.list_caps.pack(fill="both", expand=True, padx=5, pady=5)

        panes.add(frame_vols, weight=1)
        panes.add(frame_caps, weight=1)

        # ---------------------------------------------------- modo: personalizada
        self.frame_custom = ttk.Frame(self.panes_container)
        panes_c = ttk.PanedWindow(self.frame_custom, orient="horizontal")
        panes_c.pack(fill="both", expand=True)

        frame_all_caps = ttk.LabelFrame(panes_c, text="Todos los capítulos (Multi-selección)")
        self.list_all_caps = tk.Listbox(frame_all_caps, selectmode=tk.EXTENDED, font=("Arial", 9))
        self.list_all_caps.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        ttk.Button(
            frame_all_caps, text="+ Crear grupo con la selección",
            command=self._add_custom_group,
        ).pack(fill="x", padx=5, pady=5)

        frame_groups = ttk.LabelFrame(panes_c, text="Grupos personalizados a descargar")
        self.list_groups = tk.Listbox(frame_groups, font=("Arial", 9))
        self.list_groups.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        ttk.Button(
            frame_groups, text="Eliminar grupo seleccionado",
            command=self._remove_custom_group,
        ).pack(fill="x", padx=5, pady=5)

        panes_c.add(frame_all_caps, weight=1)
        panes_c.add(frame_groups, weight=1)

        self.frame_tomos.pack(fill="both", expand=True)

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

    def get_download_volumes(self):
        """Devuelve {nombre: [capitulos]} según el modo activo."""
        if self.mode.get() == "personalizada":
            return {name: caps for name, caps in self.custom_groups}
        keys = self.get_selected_keys()
        return {k: self.volumes[k] for k in keys}

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

        self.custom_groups = []
        self.list_all_caps.delete(0, tk.END)
        self.list_groups.delete(0, tk.END)
        for c in self.chapters:
            self.list_all_caps.insert(tk.END, chapter_label(c))
        self._update_next_state()

    def _finish_loading(self):
        self.spinner.stop()
        self.loading_frame.pack_forget()
        self.btn_reload.config(state="normal")
        self.btn_back.config(state="normal")
        self.combo_lang.config(state="readonly")

    def on_volume_selected(self, event):
        keys = self.get_selected_keys()
        self.list_caps.delete(0, tk.END)

        for key in keys:
            for c in self.volumes[key]:
                self.list_caps.insert(tk.END, chapter_label(c))

        self._update_next_state()

    # ---------------------------------------------------------- modo
    def _on_mode_change(self):
        if self.mode.get() == "personalizada":
            self.frame_tomos.pack_forget()
            self.frame_custom.pack(fill="both", expand=True)
        else:
            self.frame_custom.pack_forget()
            self.frame_tomos.pack(fill="both", expand=True)
        self._update_next_state()

    def _update_next_state(self):
        if self.mode.get() == "personalizada":
            enabled = len(self.custom_groups) > 0
        else:
            enabled = len(self.get_selected_keys()) > 0
        self.btn_next.config(state="normal" if enabled else "disabled")

    # ---------------------------------------------------------- grupos personalizados
    def _add_custom_group(self):
        indices = self.list_all_caps.curselection()
        if not indices:
            messagebox.showwarning("Sin selección", "Selecciona al menos un capítulo de la lista.")
            return

        selected_caps = [self.chapters[i] for i in indices]

        nums = [c["attributes"].get("chapter") for c in selected_caps if c["attributes"].get("chapter")]
        if nums:
            default_name = f"Cap {nums[0]}-{nums[-1]}" if nums[0] != nums[-1] else f"Cap {nums[0]}"
        else:
            default_name = f"Selección {len(self.custom_groups) + 1}"

        name = simpledialog.askstring(
            "Nombre del grupo",
            f"Vas a agrupar {len(selected_caps)} capítulo(s) en un tomo.\nDale un nombre:",
            initialvalue=default_name,
            parent=self,
        )
        if not name:
            return

        self.custom_groups.append((name, selected_caps))
        self.list_groups.insert(tk.END, f"{name} ({len(selected_caps)} caps)")
        self._update_next_state()

    def _remove_custom_group(self):
        sel = self.list_groups.curselection()
        if not sel:
            return
        idx = sel[0]
        del self.custom_groups[idx]
        self.list_groups.delete(idx)
        self._update_next_state()
