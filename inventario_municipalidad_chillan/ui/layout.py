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
    app.root.geometry("1280x820")
    app.root.minsize(1120, 740)

    outer = ttk.Frame(app.root)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        outer,
        highlightthickness=0,
        bg=C["gris_bg"],
    )

    sb = ttk.Scrollbar(
        outer,
        orient="vertical",
        command=canvas.yview,
    )

    app.scroll_frame = ttk.Frame(
        canvas,
        padding=(10, 8, 10, 8),
    )

    app.scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    win_id = canvas.create_window(
        (0, 0),
        window=app.scroll_frame,
        anchor="nw",
    )

    canvas.configure(yscrollcommand=sb.set)

    canvas.bind(
        "<Configure>",
        lambda e: canvas.itemconfigure(win_id, width=e.width),
    )

    def _on_mousewheel(event):
        widget = event.widget

        try:
            if widget.winfo_class() == "Text":
                return
        except Exception:
            pass

        canvas.yview_scroll(int(-1 * event.delta / 120), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    build_header(app)

    cuerpo = ttk.Frame(app.scroll_frame)
    cuerpo.pack(fill="both", expand=True)

    cuerpo.columnconfigure(0, weight=1, uniform="cols")
    cuerpo.columnconfigure(1, weight=1, uniform="cols")

    izquierda = ttk.Frame(cuerpo)
    izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

    derecha = ttk.Frame(cuerpo)
    derecha.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

    build_auto_frame(app, izquierda)
    build_monitores_frame(app, izquierda)
    build_observaciones_frame(app, izquierda)

    build_trazabilidad_frame(app, derecha)
    build_manual_frame(app, derecha)
    build_impresoras_frame(app, derecha)
    build_acciones_frame(app, derecha)