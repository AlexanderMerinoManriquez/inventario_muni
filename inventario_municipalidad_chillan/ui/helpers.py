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


def campo(parent, texto: str, variable: tk.StringVar, fila: int,
          width: int = 30, readonly: bool = False) -> ttk.Entry:
    ttk.Label(
        parent,
        text=texto,
        foreground=C["label_claro"],
        font=("Segoe UI", 9),
    ).grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

    entry = ttk.Entry(
        parent,
        textvariable=variable,
        width=width,
        state="readonly" if readonly else "normal",
    )
    entry.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)
    parent.columnconfigure(1, weight=1)
    return entry


def campo_ubicacion(app, parent, fila: int) -> ttk.Entry:
    ttk.Label(
        parent,
        text="Ubicación:",
        foreground=C["label_claro"],
        font=("Segoe UI", 9),
    ).grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

    inner = ttk.Frame(parent)
    inner.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)
    inner.columnconfigure(0, weight=1)

    entry = ttk.Entry(inner, textvariable=app.var_ubicacion, state="readonly")
    entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    ttk.Button(
        inner,
        text="✎ Editar",
        style="Small.TButton",
        command=lambda: app._habilitar_grupo_generico([entry]),
    ).grid(row=0, column=1)

    return entry