import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import C
from ui.buscador import BuscadorAutocomplete
from ui.helpers import Tooltip


def build_monitores_frame(app, parent) -> None:
    frame = app._seccion(parent, "Monitores asociados")

    btn = ttk.Button(
        frame,
        text="＋ Agregar monitor",
        style="Add.TButton",
        command=app._crear_bloque_monitor,
    )
    btn.pack(anchor="w", padx=10, pady=(4, 6))
    Tooltip(btn, "Agregar un monitor adicional al registro")

    app.monitores_container = ttk.Frame(frame)
    app.monitores_container.pack(fill="x", padx=10, pady=(0, 6))


def build_impresoras_frame(app, parent) -> None:
    frame = app._seccion(parent, "Impresoras asociadas")

    btn = ttk.Button(
        frame,
        text="＋ Agregar impresora",
        style="Add.TButton",
        command=app._crear_bloque_impresora,
    )
    btn.pack(anchor="w", padx=10, pady=(4, 6))
    Tooltip(btn, "Agregar una impresora adicional al registro")

    app.impresoras_container = ttk.Frame(frame)
    app.impresoras_container.pack(fill="x", padx=10, pady=(0, 6))


def build_observaciones_frame(app, parent) -> None:
    frame = app._seccion(parent, "Observaciones", fill="both", expand=True)

    ttk.Label(
        frame,
        text="Ej: equipo con teclado dañado, falta mouse, pendiente limpieza...",
        foreground=C["gris_placeholder"],
        font=("Segoe UI", 8),
    ).pack(anchor="w", padx=10, pady=(0, 4))

    app.txt_observaciones = ScrolledText(
    frame,
    height=5,
    wrap="word",
    font=("Segoe UI", 10),
    relief="flat",
    borderwidth=1,
    background=C["gris_panel"],
    highlightthickness=1,
    highlightbackground=C["gris_borde"],
    highlightcolor=C["rojo"],
)
    app.txt_observaciones.pack(fill="both", expand=True, padx=10, pady=(0, 8))


def build_acciones_frame(app, parent) -> None:
    tk.Frame(parent, bg=C["gris_borde"], height=1).pack(fill="x", pady=(18, 18))

    row = ttk.Frame(parent)
    row.pack(fill="x")

    app.btn_registrar = ttk.Button(
        row,
        text="  Registrar equipo  ",
        style="Primary.TButton",
        command=app.enviar_datos,
    )
    app.btn_registrar.pack(side="left")
    Tooltip(app.btn_registrar, "Enviar el registro al servidor de inventario")

    # Botón temporal de prueba. Bórralo cuando ya no lo necesites.
    ttk.Button(
        row,
        text="Probar nombre PC",
        style="Small.TButton",
        command=app.probar_nombre_equipo,
    ).pack(side="left", padx=(10, 0))

    ttk.Button(
        row,
        text="Cancelar",
        style="Danger.TButton",
        command=app.root.destroy,
    ).pack(side="right")

    app.lbl_estado = ttk.Label(
        parent,
        text="● Estado: listo",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9),
    )
    app.lbl_estado.pack(fill="x", pady=(10, 0))


def build_manual_frame(app, parent) -> None:
    frame = app._seccion(parent, "Datos del equipo y funcionario")

    label_func = ttk.Frame(frame)
    label_func.grid(row=0, column=0, sticky="nw", padx=(10, 6), pady=5)

    ttk.Label(
        label_func,
        text="Funcionario responsable:",
        foreground=C["label_claro"],
        font=("Segoe UI", 9),
    ).pack(side="left")

    ttk.Label(
        label_func,
        text="*",
        foreground=C["rojo"],
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left", padx=(2, 0))

    app.buscador_funcionario = BuscadorAutocomplete(
        frame,
        datos=app.funcionarios_data,
        variable=app.var_usuario,
        campo_busqueda="nombre",
        on_select=app._on_funcionario_seleccionado,
    )
    app.buscador_funcionario.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=5,
    )

    app._campo(frame, "RUT funcionario:", app.var_rut_funcionario, 1, readonly=True)

    app._campo(
        frame,
        "Departamento:",
        app.var_departamento_manual,
        2,
        readonly=True,
        obligatorio=True,
    )
    
    ttk.Button(
        frame,
        text="✎ Editar",
        style="Edit.TButton",
        command=lambda: app._habilitar_grupo_generico([
            app.buscador_funcionario.entry,
        ]),
    ).grid(row=0, column=2, rowspan=3, sticky="n", padx=(4, 8), pady=5)

def build_trazabilidad_frame(app, parent) -> None:
    frame = app._seccion(parent, "Trazabilidad del registro")

    ttk.Label(
        frame,
        text="Fecha y hora:",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9),
    ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=5)

    reloj = tk.Frame(frame, bg=C["gris_panel"])
    reloj.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)

    tk.Label(
        reloj,
        text="●",
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left", padx=(0, 6))

    tk.Label(
        reloj,
        textvariable=app.var_fecha_hora_visible,
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=("Segoe UI", 10, "bold"),
    ).pack(side="left")

    label_reg = ttk.Frame(frame)
    label_reg.grid(row=1, column=0, sticky="nw", padx=(10, 6), pady=5)

    ttk.Label(
        label_reg,
        text="Registrado por:",
        foreground=C["label_claro"],
        font=("Segoe UI", 9),
    ).pack(side="left")

    ttk.Label(
        label_reg,
        text="*",
        foreground=C["rojo"],
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left", padx=(2, 0))

    app.buscador_registrado_por = BuscadorAutocomplete(
        frame,
        datos=app.usuarios_sistema_data,
        variable=app.var_registrado_por,
        campo_busqueda="nombre",
        on_select=app._on_registrado_por_seleccionado,
    )
    app.buscador_registrado_por.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=5,
    )
    app._campo(frame, "RUT registrador:", app.var_rut_registrado_por, 2, readonly=True)
    ttk.Button(
        frame,
        text="✎ Editar",
        style="Edit.TButton",
        command=lambda: app._habilitar_grupo_generico([
            app.buscador_registrado_por.entry,
        ]),
    ).grid(row=1, column=2, rowspan=2, sticky="n", padx=(4, 8), pady=5)
    
    frame.columnconfigure(1, weight=1)
    app._actualizar_reloj()