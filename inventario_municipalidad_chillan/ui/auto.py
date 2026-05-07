import tkinter as tk
from tkinter import ttk

from config import C
from utils.discos_modelo import obtener_disco_principal
from utils.formato import formatear_capacidad


def build_auto_frame(app, parent) -> None:
    frame = app._seccion(
        parent,
        "Equipo principal del funcionario",
        fill="both",
        expand=False,
    )
    app.auto_frame = frame

    for fila, (clave, texto) in enumerate(app.AUTO_FIELDS):
        label_frame = ttk.Frame(frame)
        label_frame.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

        ttk.Label(
            label_frame,
            text=f"{texto}:",
            foreground=C["gris_sub"],
            font=("Segoe UI", 9),
        ).pack(side="left")

        var = tk.StringVar(value="Cargando…")
        entry = ttk.Entry(frame, textvariable=var, width=34, state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)

        app.auto_entries[clave] = {
            "var": var,
            "entry": entry,
            "label": label_frame,
        }

    app.fila_discos_inicio = len(app.AUTO_FIELDS)

    ttk.Button(
        frame,
        text="✎ Editar",
        style="Edit.TButton",
        command=app._editar_bloque_automatico,
    ).grid(
        row=0,
        column=2,
        rowspan=max(1, len(app.AUTO_FIELDS)),
        padx=(4, 8),
        pady=4,
        sticky="n",
    )

    frame.columnconfigure(1, weight=1)


def _crear_label_identificador_auto(parent, texto: str) -> ttk.Frame:
    cont = ttk.Frame(parent)

    ttk.Label(
        cont,
        text=texto,
        foreground=C["texto"],
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left")

    ttk.Label(
        cont,
        text=" ★",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left")

    return cont


def mostrar_discos_en_auto_frame(app) -> None:
    for widget in app.discos_widgets:
        widget.destroy()

    app.discos_widgets.clear()
    app.discos_entries.clear()
    app.auto_entries.pop("codigo_inventario_equipo", None)

    serial_item = app.auto_entries.get("serial")

    if serial_item:
        serial_item["label"].grid_forget()
        serial_item["entry"].grid_forget()

    fila = app.fila_discos_inicio
    disco = obtener_disco_principal(app.discos_fisicos)

    if disco:
        tipo = str(disco.get("tipo", "") or "Disco").strip()
        capacidad = formatear_capacidad(str(disco.get("capacidad", "") or "").strip())

        if capacidad:
            lbl_disco = ttk.Label(
                app.auto_frame,
                text=f"{tipo}:",
                foreground=C["gris_sub"],
                font=("Segoe UI", 9),
            )
            lbl_disco.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

            entry_disco = ttk.Entry(app.auto_frame, width=34, state="normal")
            entry_disco.insert(0, capacidad)
            entry_disco.config(state="readonly")
            entry_disco.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)

            app.discos_widgets.extend([lbl_disco, entry_disco])
            app.discos_entries.append(entry_disco)

            fila += 1

    if serial_item:
        lbl_serial = _crear_label_identificador_auto(app.auto_frame, "N° Serie:")
        lbl_serial.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

        serial_item["entry"].grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)
        serial_item["label"] = lbl_serial

        app.discos_widgets.append(lbl_serial)

        fila += 1

    lbl_codigo = _crear_label_identificador_auto(app.auto_frame, "Código inventario:")
    lbl_codigo.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

    var_codigo = tk.StringVar(value="")
    entry_codigo = ttk.Entry(
        app.auto_frame,
        textvariable=var_codigo,
        width=34,
        state="readonly",
    )
    entry_codigo.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)

    app.discos_widgets.extend([lbl_codigo, entry_codigo])
    app.auto_entries["codigo_inventario_equipo"] = {
        "var": var_codigo,
        "entry": entry_codigo,
        "label": lbl_codigo,
    }

    fila += 1

    ayuda = ttk.Label(
        app.auto_frame,
        text="★ Completa al menos uno de estos dos campos: N° serie o Código inventario.",
        foreground=C["gris_sub"],
        font=("Segoe UI", 8, "italic"),
        background=C["gris_panel"],
    )
    ayuda.grid(
        row=fila,
        column=0,
        columnspan=2,
        sticky="w",
        padx=(10, 10),
        pady=(0, 6),
    )

    app.discos_widgets.append(ayuda)