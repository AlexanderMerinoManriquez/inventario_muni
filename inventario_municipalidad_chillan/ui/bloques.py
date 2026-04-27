import tkinter as tk
from tkinter import ttk

from config import CAMPOS_MONITOR, CAMPOS_IMPRESORA

def crear_bloque(app, container, lista: list, titulo: str,
                 campos: list, renumerar, datos: dict = None) -> None:
    datos = datos or {}

    frame = ttk.LabelFrame(
        container,
        text=f"  {titulo} {len(lista) + 1}",
        style="Section.TLabelframe",
    )
    frame.pack(fill="x", pady=5)

    vars_ = {
        k: tk.StringVar(value=str(datos.get(k, "")).lower())
        for k, _ in campos
    }

    entries = {
        k: app._campo(frame, lbl, vars_[k], i, width=22, readonly=True)
        for i, (k, lbl) in enumerate(campos)
    }

    btns = ttk.Frame(frame)
    btns.grid(row=0, column=2, rowspan=len(campos), padx=(4, 8), pady=4, sticky="n")

    ttk.Button(
        btns,
        text="✎ Editar",
        style="Small.TButton",
        command=lambda e=entries: app._habilitar_grupo(e),
    ).pack(pady=(0, 4))

    ttk.Button(
        btns,
        text="✕ Quitar",
        style="Small.TButton",
        command=lambda f=frame: quitar_bloque(f, lista, renumerar),
    ).pack()

    lista.append({"frame": frame, "entries": entries, **vars_})


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
        item["frame"].configure(text=f"  Monitor {i}")


def renumerar_impresoras(app) -> None:
    for i, item in enumerate(app.impresoras_vars, 1):
        item["frame"].configure(text=f"  Impresora {i}")