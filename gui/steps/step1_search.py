import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from core.api import get_manga_by_id, search_manga

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)

class SearchStep(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.results = []
        self._build()

    def _build(self):
        ttk.Label(self, text="Paso 1: Busca tu Manga", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        search_box = ttk.Frame(self)
        search_box.pack(fill="x", pady=5)

        ttk.Label(search_box, text="Título o ID de MangaDex:").pack(side="left", padx=(0, 5))
        self.entry_search = ttk.Entry(search_box, font=("Arial", 10))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_search.bind("<Return>", lambda e: self.run_search())

        self.btn_search = ttk.Button(search_box, text="Buscar", command=self.run_search)
        self.btn_search.pack(side="left", padx=5)

        self.list_results = tk.Listbox(self, font=("Arial", 10), height=14)
        self.list_results.pack(fill="both", expand=True, pady=10)
        self.list_results.bind("<<ListboxSelect>>", self.on_manga_selected)

        nav = ttk.Frame(self)
        nav.pack(fill="x", pady=10)
        self.btn_next = ttk.Button(nav, text="Siguiente >", state="disabled", command=self.app.go_to_volumes)
        self.btn_next.pack(side="right")

    def run_search(self):
        query = self.entry_search.get().strip()
        if not query:
            return

        self.btn_search.config(state="disabled")
        self.list_results.delete(0, tk.END)
        self.btn_next.config(state="disabled")

        def worker():
            try:
                if UUID_RE.match(query):
                    results = [get_manga_by_id(query)]
                else:
                    results = search_manga(query)
                self.app.ui(self._show_results, results)
            except Exception as e:
                self.app.ui(messagebox.showerror, "Error", str(e))
            finally:
                self.app.ui(self.btn_search.config, state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def _show_results(self, results):
        self.results = results
        for item in results:
            self.list_results.insert(tk.END, f"  {item['title']}")

    def on_manga_selected(self, event):
        sel = self.list_results.curselection()
        if sel:
            self.app.selected_manga = self.results[sel[0]]
            self.btn_next.config(state="normal")
