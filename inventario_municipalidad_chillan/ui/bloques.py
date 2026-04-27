import tkinter as tk
from tkinter import ttk

from config import C, CAMPOS_MONITOR, CAMPOS_IMPRESORA


def crear_bloque(app, container, lista: list, titulo: str,
                 campos: list, renumerar, datos: dict = None) -> None:
    datos = datos or {}

    outer = tk.Frame(container, bg=C["gris_borde"], pady=1)
    outer.pack(fill="x", pady=(0, 8))

    acento = tk.Frame(outer, bg="#e8849a", width=3)
    acento.pack(side="left", fill="y")

    frame = ttk.LabelFrame(
        outer,
        text=f"  {titulo} {len(lista) + 1}  ",
        style="Section.TLabelframe",
    )
    frame.pack(side="left", fill="x", expand=True)

    vars_ = {
        k: tk.StringVar(value=str(datos.get(k, "")).lower())
        for k, _ in campos
    }

    entries = {
        k: app._campo(frame, lbl, vars_[k], i, width=34, readonly=True)
        for i, (k, lbl) in enumerate(campos)
    }
    btns = ttk.Frame(frame)
    btns.grid(
        row=0,
        column=2,
        rowspan=len(campos),
        padx=(8, 8),
        pady=6,
        sticky="n",
    )

    ttk.Button(
        btns,
        text="✎ Editar",
        style="Edit.TButton",
        command=lambda e=entries: app._habilitar_grupo(e),
    ).pack(pady=(0, 4), fill="x")

    ttk.Button(
        btns,
        text="✕ Quitar",
        style="Remove.TButton",
        command=lambda f=outer: quitar_bloque(f, lista, renumerar),
    ).pack(fill="x")

    frame.columnconfigure(1, weight=1)
    lista.append({"frame": outer, "entries": entries, **vars_})


def quitar_bloque(frame, lista: list, renumerar) -> None:
    if len(lista) == 1:
        return

    lista[:] = [item for item in lista if item["frame"] != frame]
    frame.destroy()
    renumerar()


def crear_bloque_monitor(app, datos: dict = None) -> None:
    crear_bloque(
        app,
        app.monitores_container,
        app.monitores_vars,
        "Monitor",
        CAMPOS_MONITOR,
        lambda: renumerar_monitores(app),
        datos,
    )


def crear_bloque_impresora(app, datos: dict = None) -> None:
    crear_bloque(
        app,
        app.impresoras_container,
        app.impresoras_vars,
        "Impresora",
        CAMPOS_IMPRESORA,
        lambda: renumerar_impresoras(app),
        datos,
    )


def renumerar_monitores(app) -> None:
    for i, item in enumerate(app.monitores_vars, 1):
        for child in item["frame"].winfo_children():
            if isinstance(child, ttk.LabelFrame):
                child.configure(text=f"  Monitor {i}  ")
                break


def renumerar_impresoras(app) -> None:
    for i, item in enumerate(app.impresoras_vars, 1):
        for child in item["frame"].winfo_children():
            if isinstance(child, ttk.LabelFrame):
                child.configure(text=f"  Impresora {i}  ")
                break