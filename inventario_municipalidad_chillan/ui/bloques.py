import tkinter as tk
from tkinter import ttk

from config import C, CAMPOS_MONITOR, CAMPOS_IMPRESORA


CAMPOS_IDENTIFICADOR = {
    "numero_de_serie",
    "codigo_inventario",
}


def _es_identificador(clave: str) -> bool:
    return clave in CAMPOS_IDENTIFICADOR


def _crear_label_bloque(parent, texto: str, *, identificador: bool = False) -> ttk.Frame:
    label_frame = ttk.Frame(parent)

    ttk.Label(
        label_frame,
        text=texto,
        foreground=C["texto"] if identificador else C["label_claro"],
        font=("Segoe UI", 9, "bold") if identificador else ("Segoe UI", 9),
    ).pack(side="left")

    if identificador:
        ttk.Label(
            label_frame,
            text=" ★",
            foreground=C["gris_sub"],
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

    return label_frame


def crear_bloque(app, container, lista: list, titulo: str,
                 campos: list, renumerar, datos: dict = None,
                 permitir_vacio: bool = False,
                 on_empty=None,
                 iniciar_editable: bool = False) -> None:
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
        k: tk.StringVar(value=str(datos.get(k, "") or "").strip())
        for k, _ in campos
    }

    entries = {}

    for fila, (clave, label) in enumerate(campos):
        es_id = _es_identificador(clave)

        label_frame = _crear_label_bloque(
            frame,
            label,
            identificador=es_id,
        )
        label_frame.grid(
            row=fila,
            column=0,
            sticky="w",
            padx=(10, 6),
            pady=5,
        )

        entry = ttk.Entry(
            frame,
            textvariable=vars_[clave],
            width=34,
            state="readonly",
        )
        entry.grid(
            row=fila,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=5,
        )

        entries[clave] = entry

    ayuda = ttk.Label(
        frame,
        text="★ Completa al menos uno de estos dos campos: N° serie o Código inventario.",
        foreground=C["gris_sub"],
        font=("Segoe UI", 8, "italic"),
        background=C["gris_panel"],
    )
    ayuda.grid(
        row=len(campos),
        column=0,
        columnspan=2,
        sticky="w",
        padx=(10, 10),
        pady=(0, 6),
    )

    btns = ttk.Frame(frame)
    btns.grid(
        row=0,
        column=2,
        rowspan=max(1, len(campos) + 1),
        padx=(8, 8),
        pady=6,
        sticky="ne",
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
        command=lambda f=outer: quitar_bloque(
            f,
            lista,
            renumerar,
            permitir_vacio=permitir_vacio,
            on_empty=on_empty,
        ),
    ).pack(fill="x")

    frame.columnconfigure(1, weight=1)

    lista.append({
        "frame": outer,
        "entries": entries,
        **vars_,
    })

    if iniciar_editable:
        app.root.after_idle(lambda e=entries: app._habilitar_grupo(e))


def quitar_bloque(frame, lista: list, renumerar,
                  permitir_vacio: bool = False,
                  on_empty=None) -> None:
    if len(lista) == 1 and not permitir_vacio:
        return

    lista[:] = [item for item in lista if item["frame"] != frame]
    frame.destroy()

    if lista:
        renumerar()
    elif on_empty:
        on_empty()


def crear_bloque_monitor(app, datos: dict = None) -> None:
    es_manual = datos is None

    crear_bloque(
        app,
        app.monitores_container,
        app.monitores_vars,
        "Monitor",
        CAMPOS_MONITOR,
        lambda: renumerar_monitores(app),
        datos,
        permitir_vacio=True,
        on_empty=app._mostrar_estado_monitores_vacio,
        iniciar_editable=es_manual,
    )


def crear_bloque_impresora(app, datos: dict = None) -> None:
    es_manual = datos is None

    crear_bloque(
        app,
        app.impresoras_container,
        app.impresoras_vars,
        "Impresora",
        CAMPOS_IMPRESORA,
        lambda: renumerar_impresoras(app),
        datos,
        permitir_vacio=True,
        on_empty=app._mostrar_estado_impresoras_vacio,
        iniciar_editable=es_manual,
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