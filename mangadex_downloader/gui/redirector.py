import sys
import tkinter as tk


class TextRedirector:

    def __init__(self, widget):
        self.widget = widget
        self.terminal = sys.__stdout__

    def write(self, text):
        if self.terminal:
            self.terminal.write(text)
            self.terminal.flush()
        if self.widget:
            self.widget.after(0, self._append, text)

    def _append(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)

    def flush(self):
        if self.terminal:
            self.terminal.flush()
