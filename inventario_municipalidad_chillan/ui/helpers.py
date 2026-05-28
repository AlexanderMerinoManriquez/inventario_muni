import tkinter as tk
from tkinter import ttk

from config import C


def seccion(parent, titulo, *, fill="x", expand=False, pady=(0, 14)) -> ttk.LabelFrame:
    frame = ttk.LabelFrame(
        parent,
        text=f"  {titulo}",
        style="Section.TLabelframe",
        padding=10,
    )
    frame.pack(fill=fill, expand=expand, pady=pady)
    return frame


def _crear_label_campo(parent, texto: str, *, obligatorio: bool = False) -> ttk.Frame:
    label_frame = ttk.Frame(parent)

    ttk.Label(
        label_frame,
        text=texto,
        foreground=C["texto"] if obligatorio else C["label_claro"],
        font=("Segoe UI", 9, "bold") if obligatorio else ("Segoe UI", 9),
    ).pack(side="left")

    if obligatorio:
        ttk.Label(
            label_frame,
            text=" ★",
            foreground=C["rojo"],
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

    return label_frame


def campo(parent, texto: str, variable: tk.StringVar, fila: int,
          width: int = 30, readonly: bool = False,
          obligatorio: bool = False) -> ttk.Entry:

    label_frame = _crear_label_campo(parent, texto, obligatorio=obligatorio)
    label_frame.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

    entry = ttk.Entry(
        parent,
        textvariable=variable,
        width=width,
        state="readonly" if readonly else "normal",
    )

    entry.grid(row=fila, column=1, sticky="ew", padx=(20, 14), pady=5)

    parent.columnconfigure(1, weight=1)

    return entry

class Tooltip:
    def __init__(self, widget, texto, delay=600):
        self.widget = widget
        self.texto = texto
        self.delay = delay
        self._id = None
        self._win = None

        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._cancel)
        widget.bind("<ButtonPress>", self._cancel)

    def _schedule(self, _=None):
        self._cancel()
        self._id = self.widget.after(self.delay, self._show)

    def _cancel(self, _=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self._win:
            self._win.destroy()
            self._win = None

    def _show(self):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        tk.Label(
            tw,
            text=self.texto,
            bg="#fffbe6",
            fg=C["texto"],
            font=("Segoe UI", 8),
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
        ).pack()