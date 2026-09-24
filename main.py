import tkinter as tk

from core.config import DEFAULT_OUTPUT_DIR
from gui.app import MangaWizardApp


def main():
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    MangaWizardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
