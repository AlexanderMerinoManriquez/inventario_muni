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
        ).grid(row=fila, column=0, sticky="w", padx=(10, 6), pady=5)

        var = tk.StringVar(value="Cargando…")
        entry = ttk.Entry(frame, textvariable=var, width=34, state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", padx=(0, 10), pady=5)

        app.auto_entries[clave] = {"var": var, "entry": entry}

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


def _capacidad_numero(disco: dict) -> float:
    capacidad = str(disco.get("capacidad", "") or "")
    capacidad = capacidad.upper().replace("GB", "").strip()

    try:
        return float(capacidad)
    except ValueError:
        return 0


def _disco_principal(discos: list[dict]) -> dict | None:
    if not discos:
        return None

    return sorted(
        discos,
        key=lambda d: (
            str(d.get("tipo", "")).upper() != "SSD",
            -_capacidad_numero(d),
        ),
    )[0]


def mostrar_discos_en_auto_frame(app) -> None:
    for widget in app.discos_widgets:
        widget.destroy()

    app.discos_widgets.clear()
    app.discos_entries.clear()
    app.auto_entries.pop("codigo_inventario_equipo", None)

    fila = app.fila_discos_inicio

    disco = _disco_principal(app.discos_fisicos)

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

    lbl_codigo = ttk.Label(
        app.auto_frame,
        text="Código inventario:",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9),
    )
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
    }