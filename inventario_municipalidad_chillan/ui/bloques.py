import math
import tkinter as tk
from tkinter import ttk

from config import C, CAMPOS_MONITOR, CAMPOS_IMPRESORA


CAMPO_SERIE = "numero_de_serie"


def _es_serie(clave: str) -> bool:
    return clave == CAMPO_SERIE


def _texto_visible(valor: str) -> str:
    texto = str(valor or "").strip()
    return texto if texto else "—"

def _crear_var_visible(var_origen: tk.StringVar) -> tk.StringVar:
    var_visible = tk.StringVar()

    def actualizar(*_):
        var_visible.set(_texto_visible(var_origen.get()))

    var_origen.trace_add("write", actualizar)
    actualizar()

    return var_visible

def _es_descendiente(widget, contenedor) -> bool:
    if not widget or not contenedor:
        return False

    actual = widget

    while actual is not None:
        if actual == contenedor:
            return True

        try:
            actual = actual.master
        except Exception:
            return False

    return False

def _crear_tarjeta(parent) -> tuple[tk.Frame, tk.Frame]:
    outer = tk.Frame(
        parent,
        bg=C["gris_borde"],
        bd=0,
        highlightthickness=0,
    )
    outer.pack(fill="x", pady=(0, 7), padx=0)

    inner = tk.Frame(
        outer,
        bg=C["blanco"],
        bd=0,
        padx=10,
        pady=7,
    )
    inner.pack(fill="x", padx=1, pady=1)

    return outer, inner

def _crear_header_tarjeta(parent, titulo: str) -> tuple[tk.Label, tk.Frame]:
    header = tk.Frame(parent, bg=C["blanco"], bd=0)
    header.pack(fill="x", pady=(0, 4))

    izquierda = tk.Frame(header, bg=C["blanco"], bd=0)
    izquierda.pack(side="left", fill="x", expand=True)

    indicador = tk.Frame(
        izquierda,
        bg=C["rojo"],
        width=3,
        height=16,
    )
    indicador.pack(side="left", padx=(0, 7))
    indicador.pack_propagate(False)

    lbl_titulo = tk.Label(
        izquierda,
        text=titulo,
        bg=C["blanco"],
        fg=C["rojo"],
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    )
    lbl_titulo.pack(side="left")

    btns = tk.Frame(header, bg=C["blanco"], bd=0)
    btns.pack(side="right")

    return lbl_titulo, btns

def _crear_contenedor_dos_columnas(parent) -> tuple[tk.Frame, tk.Frame, tk.Frame]:
    contenedor = tk.Frame(parent, bg=C["blanco"], bd=0)
    contenedor.pack(fill="x", pady=(2, 0))

    contenedor.columnconfigure(0, weight=1, uniform="mitades")
    contenedor.columnconfigure(1, weight=1, uniform="mitades")

    izquierda = tk.Frame(contenedor, bg=C["blanco"], bd=0)
    izquierda.grid(row=0, column=0, sticky="new", padx=(0, 8))

    derecha = tk.Frame(contenedor, bg=C["blanco"], bd=0)
    derecha.grid(row=0, column=1, sticky="new", padx=(8, 0))

    for panel in (izquierda, derecha):
        panel.columnconfigure(0, weight=0)
        panel.columnconfigure(1, weight=1)

    return contenedor, izquierda, derecha

def _crear_label_obligatorio(parent, texto: str, fila: int) -> None:
    cont = tk.Frame(parent, bg=C["blanco"])
    cont.grid(
        row=fila,
        column=0,
        sticky="w",
        padx=(4, 5),
        pady=2,
    )

    tk.Label(
        cont,
        text=texto,
        bg=C["blanco"],
        fg=C["texto"],
        font=("Segoe UI", 8, "bold"),
        anchor="w",
    ).pack(side="left")

    tk.Label(
        cont,
        text=" *",
        bg=C["blanco"],
        fg=C["rojo"],
        font=("Segoe UI", 8, "bold"),
        anchor="w",
    ).pack(side="left")

def _crear_label_normal(parent, texto: str, fila: int, *, pady: int = 2) -> None:
    tk.Label(
        parent,
        text=texto,
        bg=C["blanco"],
        fg=C["label_claro"],
        font=("Segoe UI", 8),
        anchor="w",
    ).grid(
        row=fila,
        column=0,
        sticky="w",
        padx=(4, 5),
        pady=pady,
    )
    
def _crear_fila_resumen(
    parent,
    etiqueta: str,
    variable: tk.StringVar,
    fila: int,
    *,
    obligatorio: bool = False,
) -> None:
    if obligatorio:
        _crear_label_obligatorio(parent, etiqueta, fila)
    else:
        _crear_label_normal(parent, etiqueta, fila)

    tk.Label(
        parent,
        textvariable=_crear_var_visible(variable),
        bg=C["blanco"],
        fg=C["texto"],
        font=("Segoe UI", 8),
        anchor="w",
    ).grid(
        row=fila,
        column=1,
        sticky="w",
        padx=(0, 8),
        pady=2,
    )

def _crear_fila_editor(
    parent,
    etiqueta: str,
    entry: ttk.Entry,
    fila: int,
    *,
    obligatorio: bool = False,
) -> None:
    if obligatorio:
        _crear_label_obligatorio(parent, etiqueta, fila)
    else:
        _crear_label_normal(parent, etiqueta, fila, pady=3)

    entry.grid(
        row=fila,
        column=1,
        sticky="ew",
        padx=(0, 8),
        pady=3,
    )

def crear_bloque(
    app,
    container,
    lista: list,
    titulo: str,
    campos: list,
    renumerar,
    datos: dict = None,
    permitir_vacio: bool = False,
    on_empty=None,
    iniciar_editable: bool = False,
) -> None:
    datos = datos or {}

    outer, card = _crear_tarjeta(container)

    vars_ = {
        clave: tk.StringVar(value=str(datos.get(clave, "") or "").strip())
        for clave, _ in campos
    }

    entries = {}

    item = {
        "frame": outer,
        "card": card,
        "entries": entries,
        "modo_edicion": False,
        **vars_,
    }

    lbl_titulo, btns = _crear_header_tarjeta(
        card,
        f"{titulo} {len(lista) + 1}",
    )

    btn_editar = ttk.Button(
        btns,
        text="✎ Editar",
        style="Edit.TButton",
        width=9,
    )
    btn_editar.pack(side="left", padx=(0, 4))

    btn_quitar = ttk.Button(
        btns,
        text="✕ Quitar",
        style="Remove.TButton",
        width=9,
        command=lambda f=outer: quitar_bloque(
            f,
            lista,
            renumerar,
            permitir_vacio=permitir_vacio,
            on_empty=on_empty,
        ),
    )
    btn_quitar.pack(side="left")

    resumen_contenedor, resumen_izq, resumen_der = _crear_contenedor_dos_columnas(card)
    editor_contenedor, editor_izq, editor_der = _crear_contenedor_dos_columnas(card)
    editor_contenedor.pack_forget()

    mitad = math.ceil(len(campos) / 2)

    for i, (clave, etiqueta) in enumerate(campos):
        fila = i % mitad
        panel = resumen_izq if i < mitad else resumen_der
        obligatorio = _es_serie(clave)

        _crear_fila_resumen(
            panel,
            etiqueta,
            vars_[clave],
            fila,
            obligatorio=obligatorio,
        )

    for i, (clave, etiqueta) in enumerate(campos):
        fila = i % mitad
        panel = editor_izq if i < mitad else editor_der
        obligatorio = _es_serie(clave)

        entry = ttk.Entry(
            panel,
            textvariable=vars_[clave],
            width=24,
            state="readonly",
        )

        entries[clave] = entry

        _crear_fila_editor(
            panel,
            etiqueta,
            entry,
            fila,
            obligatorio=obligatorio,
        )

    ayuda = tk.Label(
        editor_contenedor,
        text="* N° de serie obligatorio.",
        bg=C["blanco"],
        fg=C["rojo"],
        font=("Segoe UI", 8, "italic"),
        anchor="w",
    )
    ayuda.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="w",
        padx=(4, 4),
        pady=(4, 0),
    )

    def mostrar_resumen() -> None:
        item["modo_edicion"] = False

        for entry in entries.values():
            entry.config(state="readonly")

        editor_contenedor.pack_forget()
        resumen_contenedor.pack(fill="x", pady=(2, 0))
        btn_editar.config(text="✎ Editar")

    def mostrar_edicion() -> None:
        item["modo_edicion"] = True

        resumen_contenedor.pack_forget()
        editor_contenedor.pack(fill="x", pady=(2, 0))

        for entry in entries.values():
            entry.config(state="normal")

        btn_editar.config(text="✓ Listo")

        primer = next(iter(entries.values()), None)

        if primer:
            primer.focus_set()
            primer.icursor("end")

    def alternar() -> None:
        if item["modo_edicion"]:
            mostrar_resumen()
        else:
            mostrar_edicion()

    def revisar_click_fuera(event) -> None:
        if not item["modo_edicion"]:
            return

        widget = event.widget

        if _es_descendiente(widget, outer):
            return

        mostrar_resumen()

    def revisar_focus_out(_=None) -> None:
        def cerrar_si_corresponde():
            if not item["modo_edicion"]:
                return

            foco = app.root.focus_get()

            if _es_descendiente(foco, outer):
                return

            mostrar_resumen()

        app.root.after_idle(cerrar_si_corresponde)

    btn_editar.config(command=alternar)

    for entry in entries.values():
        entry.bind("<FocusOut>", revisar_focus_out, add="+")
        entry.bind("<Return>", lambda _=None: mostrar_resumen(), add="+")

    app.root.bind("<Button-1>", revisar_click_fuera, add="+")

    item["mostrar_edicion"] = mostrar_edicion
    item["mostrar_resumen"] = mostrar_resumen
    item["label_titulo"] = lbl_titulo
    item["btn_editar"] = btn_editar

    lista.append(item)

    if iniciar_editable:
        app.root.after_idle(mostrar_edicion)

def quitar_bloque(
    frame,
    lista: list,
    renumerar,
    permitir_vacio: bool = False,
    on_empty=None,
) -> None:
    if len(lista) == 1 and not permitir_vacio:
        return

    lista[:] = [item for item in lista if item["frame"] != frame]
    frame.destroy()

    if lista:
        renumerar()
    elif on_empty:
        on_empty()

def crear_bloque_monitor(app, datos: dict = None) -> None:
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
        iniciar_editable=(datos is None),
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
        permitir_vacio=True,
        on_empty=app._mostrar_estado_impresoras_vacio,
        iniciar_editable=(datos is None),
    )

def renumerar_monitores(app) -> None:
    for i, item in enumerate(app.monitores_vars, 1):
        item["label_titulo"].config(text=f"Monitor {i}")


def renumerar_impresoras(app) -> None:
    for i, item in enumerate(app.impresoras_vars, 1):
        item["label_titulo"].config(text=f"Impresora {i}")