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
        ttk.Label(cont, text=" *", foreground=C["rojo"], font=LABEL_BOLD_FONT).pack(side="left")
    return cont


def _mensaje_obligatorios(parent, fila: int, columna: int = 0, columnspan: int = 2) -> None:
    ttk.Label(
        parent,
        text="* Campos obligatorios. Deben seleccionarse desde la lista.",
        foreground=C["rojo"],
        font=("Segoe UI", 8, "italic"),
    ).grid(
        row=fila, column=columna, columnspan=columnspan,
        sticky="w", padx=(10, 10), pady=(0, 6),
    )


def build_monitores_frame(app, parent) -> None:
    frame = app._seccion(parent, "Monitores asignados")

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
        font=LABEL_FONT,
    )
    app.lbl_monitores_vacio.pack(fill="x", padx=10, pady=(0, 8))
    app.lbl_monitores_vacio.pack_forget()

    app.monitores_container = ttk.Frame(frame)
    app.monitores_container.pack(fill="x", padx=10, pady=(0, 6))
    app.monitores_container.pack_forget()


def build_impresoras_frame(app, parent) -> None:
    frame = app._seccion(parent, "Impresoras asignadas")

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
        font=LABEL_FONT,
    )
    app.lbl_impresoras_vacio.pack(fill="x", padx=10, pady=(0, 8))
    app.lbl_impresoras_vacio.pack_forget()

    app.impresoras_container = ttk.Frame(frame)
    app.impresoras_container.pack(fill="x", padx=10, pady=(0, 6))
    app.impresoras_container.pack_forget()


def build_observaciones_frame(app, parent) -> None:
    frame = app._seccion(parent, "Observaciones del inventario", fill="both", expand=True)

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
    frame = app._seccion(parent, "Departamento y funcionario asignado")
    frame.columnconfigure(1, weight=1)

    _label_campo(frame, "Departamento:", obligatorio=True).grid(
        row=0, column=0, sticky="w", padx=(10, 6), pady=5
    )
    app.buscador_departamento = BuscadorAutocomplete(
        frame,
        datos=app.departamentos_data,
        variable=app.var_departamento_funcionario,
        campo_busqueda="nombre",
        campo_valor="nombre",
        formato_resultado=lambda d: d.get("nombre", ""),
        on_select=app._on_departamento_seleccionado,
        on_clear=app._limpiar_departamento,
        permitir_manual=False,
    )
    app.buscador_departamento.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=5)

    _label_campo(frame, "Funcionario responsable:", obligatorio=True).grid(
        row=1, column=0, sticky="w", padx=(10, 6), pady=5
    )
    app.buscador_funcionario = BuscadorAutocomplete(
        frame,
        datos=app.funcionarios_data,
        variable=app.var_usuario,
        campo_busqueda="nombre",
        campo_valor="nombre",
        campos_extra_busqueda=["rut"],
        formato_resultado=lambda p: f"{p.get('nombre', '')} — {p.get('rut', '')}",
        on_select=app._on_funcionario_seleccionado,
        on_clear=app._limpiar_funcionario,
        permitir_manual=False,
    )
    app.buscador_funcionario.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=5)

    app.entry_rut_funcionario = app._campo(
        frame, "RUT funcionario:", app.var_rut_funcionario, 2,
        readonly=True, obligatorio=False,
    )

    _mensaje_obligatorios(frame, fila=3, columnspan=2)


def build_trazabilidad_frame(app, parent) -> None:
    frame = app._seccion(parent, "Datos del registrador")
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Fecha y hora:", foreground=C["gris_sub"], font=LABEL_FONT).grid(
        row=0, column=0, sticky="w", padx=(10, 6), pady=5
    )

    reloj = tk.Frame(frame, bg=C["gris_panel"])
    reloj.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)

    tk.Label(reloj, text="●", bg=C["gris_panel"], fg=C["rojo"], font=LABEL_BOLD_FONT).pack(
        side="left", padx=(0, 6)
    )
    tk.Label(
        reloj,
        textvariable=app.var_fecha_hora_visible,
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=("Segoe UI", 10, "bold"),
    ).pack(side="left")

    _label_campo(frame, "RUT registrador:", obligatorio=True).grid(
        row=1, column=0, sticky="w", padx=(10, 6), pady=5
    )
    app.buscador_registrador = BuscadorAutocomplete(
        frame,
        datos=app.usuarios_sistema_data,
        variable=app.var_rut_registrador,
        campo_busqueda="rut",
        campo_valor="rut",
        campos_extra_busqueda=["nombre"],
        formato_resultado=lambda p: f"{p.get('rut', '')} — {p.get('nombre', '')}",
        on_select=app._on_registrador_seleccionado,
        on_clear=app._limpiar_registrador,
        permitir_manual=False,
    )
    app.buscador_registrador.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=5)

    app.entry_nombre_registrador = app._campo(
        frame, "Nombre registrador:", app.var_nombre_registrador, 2,
        readonly=True, obligatorio=False,
    )

    _mensaje_obligatorios(frame, fila=3, columnspan=2)
    app._actualizar_reloj()
