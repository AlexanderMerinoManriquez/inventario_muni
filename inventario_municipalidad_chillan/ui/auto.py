import tkinter as tk
from tkinter import ttk

from config import C
from utils.formato import formatear_capacidad


def build_auto_frame(app, parent) -> None:
    frame = app._seccion(
        parent,
        "Datos detectados automáticamente",
        fill="both",
        expand=False,
    )
    app.auto_frame = frame

    for fila, (clave, texto) in enumerate(app.AUTO_FIELDS):
        ttk.Label(
            frame,
            text=f"{texto}:",
            foreground=C["gris_sub"],
            font=("Segoe UI", 9),
        ).grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=4)

        var = tk.StringVar(value="Cargando…")
        entry = ttk.Entry(frame, textvariable=var, width=34, state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=4)

        app.auto_entries[clave] = {"var": var, "entry": entry}

    app.fila_discos_inicio = len(app.AUTO_FIELDS)

    ttk.Button(
        frame,
        text="✎ Editar",
        style="Small.TButton",
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


def mostrar_discos_en_auto_frame(app) -> None:
    for widget in app.discos_widgets:
        widget.destroy()

    app.discos_widgets.clear()
    app.discos_entries.clear()

    for i, disco in enumerate(app.discos_fisicos):
        tipo = str(disco.get("tipo", "") or "Disco").strip()
        capacidad = formatear_capacidad(str(disco.get("capacidad", "") or "").strip())

        if not capacidad:
            continue

        disco["capacidad"] = capacidad
        fila = app.fila_discos_inicio + i

        lbl = ttk.Label(
            app.auto_frame,
            text=f"{tipo}:",
            foreground=C["gris_sub"],
            font=("Segoe UI", 9),
        )
        lbl.grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=4)

        entry = ttk.Entry(app.auto_frame, width=34, state="normal")
        entry.insert(0, capacidad)
        entry.config(state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=4)

        app.discos_widgets.extend([lbl, entry])
        app.discos_entries.append(entry)