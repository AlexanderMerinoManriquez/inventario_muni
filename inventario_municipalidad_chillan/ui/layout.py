import tkinter as tk
from tkinter import ttk

from config import C
from ui.header import build_header
from ui.auto import build_auto_frame
from ui.secciones import (
    build_monitores_frame,
    build_impresoras_frame,
    build_observaciones_frame,
    build_acciones_frame,
    build_manual_frame,
    build_trazabilidad_frame,
)


def construir_interfaz(app) -> None:
    outer = ttk.Frame(app.root)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, highlightthickness=0, bg=C["gris_bg"])
    sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)

    app.scroll_frame = ttk.Frame(canvas, padding=20)
    app.scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    win_id = canvas.create_window((0, 0), window=app.scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win_id, width=e.width))
    canvas.bind_all(
        "<MouseWheel>",
        lambda e: canvas.yview_scroll(int(-1 * e.delta / 120), "units"),
    )

    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    build_header(app)

    cuerpo = ttk.Frame(app.scroll_frame)
    cuerpo.pack(fill="both", expand=True)

    izq = ttk.Frame(cuerpo)
    izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    der = ttk.Frame(cuerpo)
    der.pack(side="left", fill="both", expand=True, padx=(10, 0))

    build_auto_frame(app, izq)
    build_monitores_frame(app, izq)

    build_trazabilidad_frame(app, der)
    build_manual_frame(app, der)
    build_impresoras_frame(app, der)
    build_observaciones_frame(app, der)
    build_acciones_frame(app, der)