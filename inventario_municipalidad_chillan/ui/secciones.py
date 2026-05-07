import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import C
from ui.buscador import BuscadorAutocomplete
from ui.helpers import Tooltip

LABEL_FONT = ("Segoe UI", 9)
LABEL_SMALL_FONT = ("Segoe UI", 8)
LABEL_BOLD_FONT = ("Segoe UI", 9, "bold")


def _label_campo(parent, texto: str, *, obligatorio: bool = False):
    cont = ttk.Frame(parent)

    ttk.Label(
        cont,
        text=texto,
        foreground=C["texto"] if obligatorio else C["label_claro"],
        font=LABEL_BOLD_FONT if obligatorio else LABEL_FONT,
    ).pack(side="left")

    if obligatorio:
        ttk.Label(
            cont,
            text=" ★",
            foreground=C["rojo"],
            font=LABEL_BOLD_FONT,
        ).pack(side="left")

    return cont


def _boton_editar(parent, texto_tooltip: str, command):
    btn = ttk.Button(
        parent,
        text="✎ Editar",
        style="Edit.TButton",
        command=command,
    )
    Tooltip(btn, texto_tooltip)
    return btn

def _crear_frame_activos(app, parent, titulo: str, texto_boton: str, command, tooltip: str):
    frame = app._seccion(parent, titulo)

    btn = ttk.Button(
        frame,
        text=texto_boton,
        style="Add.TButton",
        command=command,
    )
    btn.pack(anchor="w", padx=10, pady=(4, 6))
    Tooltip(btn, tooltip)

    container = ttk.Frame(frame)
    container.pack(fill="x", padx=10, pady=(0, 6))

    return container


def build_monitores_frame(app, parent) -> None:
    frame = app._seccion(parent, "Monitores asociados")

    btn = ttk.Button(
        frame,
        text="＋ Agregar monitor",
        style="Add.TButton",
        command=app._crear_bloque_monitor,
    )
    btn.pack(anchor="w", padx=10, pady=(4, 6))
    Tooltip(btn, "Agregar un monitor manualmente si corresponde")

    app.lbl_monitores_vacio = ttk.Label(
        frame,
        text="No se detectaron monitores. Puedes agregar uno manualmente si corresponde.",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9),
    )
    app.lbl_monitores_vacio.pack(fill="x", padx=10, pady=(0, 8))
    app.lbl_monitores_vacio.pack_forget()

    app.monitores_container = ttk.Frame(frame)
    app.monitores_container.pack(fill="x", padx=10, pady=(0, 6))
    app.monitores_container.pack_forget()


def build_impresoras_frame(app, parent) -> None:
    frame = app._seccion(parent, "Impresoras asociadas")

    btn = ttk.Button(
        frame,
        text="＋ Agregar impresora",
        style="Add.TButton",
        command=app._crear_bloque_impresora,
    )
    btn.pack(anchor="w", padx=10, pady=(4, 6))
    Tooltip(btn, "Agregar una impresora manualmente si corresponde")

    app.lbl_impresoras_vacio = ttk.Label(
        frame,
        text="No se detectaron impresoras activas. Puedes agregar una manualmente si corresponde.",
        foreground=C["gris_sub"],
        font=("Segoe UI", 9),
    )
    app.lbl_impresoras_vacio.pack(fill="x", padx=10, pady=(0, 8))
    app.lbl_impresoras_vacio.pack_forget()

    app.impresoras_container = ttk.Frame(frame)
    app.impresoras_container.pack(fill="x", padx=10, pady=(0, 6))
    app.impresoras_container.pack_forget()


def build_observaciones_frame(app, parent) -> None:
    frame = app._seccion(parent, "Observaciones", fill="both", expand=True)

    ttk.Label(
        frame,
        text="Ej: equipo con teclado dañado, falta mouse, pendiente limpieza…",
        foreground=C["gris_placeholder"],
        font=LABEL_SMALL_FONT,
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
        font=LABEL_FONT,
    )
    app.lbl_estado.pack(fill="x", pady=(10, 0))


def build_manual_frame(app, parent) -> None:
    frame = app._seccion(parent, "Datos del equipo y funcionario")
    frame.columnconfigure(1, weight=1)

    _label_campo(
        frame,
        "Funcionario responsable:",
        obligatorio=True,
    ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=5)

    app.buscador_funcionario = BuscadorAutocomplete(
        frame,
        datos=app.funcionarios_data,
        variable=app.var_usuario,
        campo_busqueda="nombre",
        campo_valor="nombre",
        campos_extra_busqueda=["rut", "departamento"],
        formato_resultado=lambda p: (
            f"{p.get('nombre', '')} — {p.get('rut', '')} — {p.get('departamento', '')}"
        ),
        on_select=app._on_funcionario_seleccionado,
        on_clear=app._limpiar_funcionario,
    )
    app.buscador_funcionario.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=5)

    app.entry_rut_funcionario = app._campo(
        frame,
        "RUT funcionario:",
        app.var_rut_funcionario,
        1,
        readonly=True,
        obligatorio=True,
    )

    app.entry_departamento_manual = app._campo(
        frame,
        "Departamento:",
        app.var_departamento_manual,
        2,
        readonly=True,
        obligatorio=True,
    )

    btn_editar_func = _boton_editar(
        frame,
        "Editar RUT y departamento del funcionario",
        lambda: app._habilitar_grupo_generico([
            app.entry_rut_funcionario,
            app.entry_departamento_manual,
        ]),
    )
    btn_editar_func.grid(
        row=1,
        column=2,
        rowspan=2,
        sticky="n",
        padx=(0, 8),
        pady=5,
    )
def build_trazabilidad_frame(app, parent) -> None:
    frame = app._seccion(parent, "Trazabilidad del registro")
    frame.columnconfigure(1, weight=1)

    ttk.Label(
        frame,
        text="Fecha y hora:",
        foreground=C["gris_sub"],
        font=LABEL_FONT,
    ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=5)

    reloj = tk.Frame(frame, bg=C["gris_panel"])
    reloj.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)

    tk.Label(
        reloj,
        text="●",
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=LABEL_BOLD_FONT,
    ).pack(side="left", padx=(0, 6))

    tk.Label(
        reloj,
        textvariable=app.var_fecha_hora_visible,
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=("Segoe UI", 10, "bold"),
    ).pack(side="left")

    _label_campo(
        frame,
        "RUT registrador:",
        obligatorio=True,
    ).grid(row=1, column=0, sticky="w", padx=(10, 6), pady=5)

    app.buscador_registrado_por = BuscadorAutocomplete(
        frame,
        datos=app.usuarios_sistema_data,
        variable=app.var_rut_registrado_por,
        campo_busqueda="rut",
        campo_valor="rut",
        campos_extra_busqueda=["nombre"],
        formato_resultado=lambda p: f"{p.get('rut', '')} — {p.get('nombre', '')}",
        on_select=app._on_registrado_por_seleccionado,
        on_clear=app._limpiar_registrador,
    )
    app.buscador_registrado_por.grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=5)

    app.entry_nombre_registrador = app._campo(
        frame,
        "Nombre registrador:",
        app.var_registrado_por,
        2,
        readonly=True,
        obligatorio=True,
    )

    btn_editar_reg = _boton_editar(
        frame,
        "Editar nombre del registrador",
        lambda: app._habilitar_grupo_generico([
            app.entry_nombre_registrador,
        ]),
    )
    btn_editar_reg.grid(
        row=2,
        column=2,
        sticky="n",
        padx=(0, 8),
        pady=5,
    )

    app._actualizar_reloj()