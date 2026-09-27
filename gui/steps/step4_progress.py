import threading
from tkinter import ttk, messagebox, scrolledtext

from core.downloader import create_volume_files


class ProgressStep(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        ttk.Label(self, text="Paso 4: Descargando y procesando...", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        self.lbl_status = ttk.Label(self, text="Iniciando...", font=("Arial", 10))
        self.lbl_status.pack(anchor="w", pady=2)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", pady=10)

        ttk.Label(self, text="Registro de Actividad:").pack(anchor="w", pady=(10, 2))
        self.log_text = scrolledtext.ScrolledText(self, height=15, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, pady=5)

        nav = ttk.Frame(self)
        nav.pack(fill="x", pady=10)
        self.btn_restart = ttk.Button(nav, text="<< Descargar otra serie", state="disabled",
                                      command=lambda: self.app.show_step(1))
        self.btn_restart.pack(side="left")

    def _update(self, pct, text):
        self.progress["value"] = pct
        self.lbl_status.config(text=text)

    def start(self, manga_title, volumes, language, output_dir, export_epub, export_pdf):
        """volumes: dict {nombre_tomo: [capítulos]}"""
        self.btn_restart.config(state="disabled")
        total_vols = len(volumes)

        def worker():
            try:
                for idx, (vol_name, chapters) in enumerate(volumes.items(), start=1):
                    def on_progress(cur, tot, msg, idx=idx):
                        pct = (cur / tot) * 100 if tot > 0 else 0
                        self.app.ui(self._update, pct, f"[Tomo {idx}/{total_vols}] {msg}")

                    create_volume_files(
                        manga_title=manga_title,
                        volume=vol_name,
                        chapters=chapters,
                        language=language,
                        output_base_dir=output_dir,
                        export_epub=export_epub,
                        export_pdf_flag=export_pdf,
                        progress_callback=on_progress,
                    )

                self.app.ui(self._update, 100, "¡Proceso completado con éxito!")
                self.app.ui(messagebox.showinfo, "Completado",
                            f"Se han procesado {total_vols} tomo(s).\nUbicación: {output_dir}")
            except Exception as e:
                print(f"\n[ERROR FATAL] {e}")
                self.app.ui(messagebox.showerror, "Error", str(e))
            finally:
                self.app.ui(self.btn_restart.config, state="normal")

        threading.Thread(target=worker, daemon=True).start()
