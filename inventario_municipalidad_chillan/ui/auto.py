import tkinter as tk
from tkinter import ttk

from config import C
from utils.discos_modelo import obtener_disco_principal
from utils.formato import formatear_capacidad


AUTO_RESUMEN_CAMPOS = [
    ("nombre_pc", "Nombre PC"),
    ("marca", "Marca"),
    ("modelo", "Modelo"),
    ("tipo", "Tipo"),
    ("sistema_operativo", "Sistema operativo"),
    ("cpu", "Procesador"),
    ("ram", "RAM"),
    ("ip", "IP"),
    ("anydesk", "AnyDesk"),
    ("disco_principal", "Disco principal"),
    ("serial", "N° Serie"),
    ("codigo_inventario", "Código inventario"),
]

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

def _crear_tarjeta(parent, *, visible: bool = True) -> tuple[tk.Frame, tk.Frame]:
    outer = tk.Frame(
        parent,
        bg=C["gris_borde"],
        bd=0,
        highlightthickness=0,
    )

    inner = tk.Frame(
        outer,
        bg=C["blanco"],
        bd=0,
        padx=10,
        pady=8,
    )
    inner.pack(fill="x", padx=1, pady=1)

    if visible:
        outer.pack(fill="x", padx=6, pady=(0, 6))

    return outer, inner

def _crear_label_obligatorio(parent, texto: str, fila: int, columna: int) -> None:
    cont = tk.Frame(parent, bg=C["blanco"])
    cont.grid(
        row=fila,
        column=columna,
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

def _crear_label_normal(parent, texto: str, fila: int, columna: int, *, pady: int = 2) -> None:
    tk.Label(
        parent,
        text=texto,
        bg=C["blanco"],
        fg=C["label_claro"],
        font=("Segoe UI", 8),
        anchor="w",
    ).grid(
        row=fila,
        column=columna,
        sticky="w",
        padx=(4, 5),
        pady=pady,
    )

def _crear_fila_resumen(
    parent,
    etiqueta: str,
    variable: tk.StringVar,
    fila: int,
    columna: int,
    *,
    obligatorio: bool = False,
) -> None:
    base_col = columna * 2

    texto_label = f"{etiqueta}:"

    if obligatorio:
        _crear_label_obligatorio(parent, texto_label, fila, base_col)
    else:
        _crear_label_normal(parent, texto_label, fila, base_col)

    tk.Label(
        parent,
        textvariable=_crear_var_visible(variable),
        bg=C["blanco"],
        fg=C["texto"],
        font=("Segoe UI", 8),
        anchor="w",
    ).grid(
        row=fila,
        column=base_col + 1,
        sticky="ew",
        padx=(0, 16),
        pady=2,
    )

def _crear_fila_editor(
    parent,
    etiqueta: str,
    entry: ttk.Entry,
    fila: int,
    columna: int,
    *,
    obligatorio: bool = False,
) -> None:
    base_col = columna * 2

    texto_label = f"{etiqueta}:"

    if obligatorio:
        _crear_label_obligatorio(parent, texto_label, fila, base_col)
    else:
        _crear_label_normal(parent, texto_label, fila, base_col, pady=3)

    entry.grid(
        row=fila,
        column=base_col + 1,
        sticky="ew",
        padx=(0, 16),
        pady=3,
    )

def alternar_auto(app, editar: bool | None = None) -> None:
    actual = bool(getattr(app, "auto_en_edicion", False))
    nuevo_estado = not actual if editar is None else bool(editar)

    app.auto_en_edicion = nuevo_estado

    if nuevo_estado:
        if hasattr(app, "auto_summary_outer"):
            app.auto_summary_outer.pack_forget()

        if hasattr(app, "auto_edit_outer"):
            app.auto_edit_outer.pack(fill="x", padx=6, pady=(0, 6))

        for item in app.auto_entries.values():
            entry = item.get("entry")

            if entry:
                entry.config(state="normal")

        if hasattr(app, "btn_auto_editar"):
            app.btn_auto_editar.config(text="✓ Listo")
        item_nombre_pc = app.auto_entries.get("nombre_pc")
        entry_nombre_pc = item_nombre_pc.get("entry") if item_nombre_pc else None

        if entry_nombre_pc:
            entry_nombre_pc.focus_set()
            entry_nombre_pc.icursor("end")

        return

    for item in app.auto_entries.values():
        entry = item.get("entry")

        if entry:
            entry.config(state="readonly")

    if hasattr(app, "auto_edit_outer"):
        app.auto_edit_outer.pack_forget()

    if hasattr(app, "auto_summary_outer"):
        app.auto_summary_outer.pack(fill="x", padx=6, pady=(0, 6))

    if hasattr(app, "btn_auto_editar"):
        app.btn_auto_editar.config(text="✎ Editar")

def _instalar_cierre_al_hacer_click_fuera(app) -> None:
    if getattr(app, "_auto_click_fuera_instalado", False):
        return

    def revisar_click(event):
        if not getattr(app, "auto_en_edicion", False):
            return

        widget = event.widget

        if _es_descendiente(widget, getattr(app, "auto_frame", None)):
            return

        alternar_auto(app, False)

    app.root.bind("<Button-1>", revisar_click, add="+")
    app._auto_click_fuera_instalado = True

def build_auto_frame(app, parent) -> None:
    frame = app._seccion(parent, "Equipo asignado", fill="x", expand=False, pady=(0, 10))
    app.auto_frame = frame
    app.auto_en_edicion = False

    header = tk.Frame(frame, bg=C["gris_panel"], bd=0)
    header.pack(fill="x", padx=6, pady=(0, 4))

    tk.Label(
        header,
        text="Datos detectados automáticamente",
        bg=C["gris_panel"],
        fg=C["gris_sub"],
        font=("Segoe UI", 8),
    ).pack(side="left")

    app.btn_auto_editar = ttk.Button(
        header,
        text="✎ Editar",
        style="Edit.TButton",
        command=lambda: alternar_auto(app),
    )
    app.btn_auto_editar.pack(side="right")

    app.auto_summary_outer, app.auto_summary_card = _crear_tarjeta(frame, visible=True)
    app.auto_edit_outer, app.auto_edit_card = _crear_tarjeta(frame, visible=False)

    for clave, _texto in app.AUTO_FIELDS:
        var = tk.StringVar(value="Cargando…")

        entry = ttk.Entry(
            app.auto_edit_card,
            textvariable=var,
            width=28,
            state="readonly",
        )

        app.auto_entries[clave] = {
            "var": var,
            "entry": entry,
            "label": None,
        }

    var_disco = tk.StringVar(value="Cargando…")
    entry_disco = ttk.Entry(
        app.auto_edit_card,
        textvariable=var_disco,
        width=28,
        state="readonly",
    )

    app.auto_entries["disco_principal"] = {
        "var": var_disco,
        "entry": entry_disco,
        "label": None,
    }

    app.discos_entries.append(entry_disco)

    var_codigo = tk.StringVar(value="")
    entry_codigo = ttk.Entry(
        app.auto_edit_card,
        textvariable=var_codigo,
        width=28,
        state="readonly",
    )

    app.auto_entries["codigo_inventario"] = {
        "var": var_codigo,
        "entry": entry_codigo,
        "label": None,
    }

    for i, (clave, etiqueta) in enumerate(AUTO_RESUMEN_CAMPOS):
        item = app.auto_entries.get(clave)

        if not item:
            continue

        fila = i % 6
        columna = i // 6

        _crear_fila_resumen(
            app.auto_summary_card,
            etiqueta,
            item["var"],
            fila,
            columna,
            obligatorio=(clave == "serial"),
        )

    app.auto_summary_card.columnconfigure(1, weight=1)
    app.auto_summary_card.columnconfigure(3, weight=1)

    for i, (clave, etiqueta) in enumerate(AUTO_RESUMEN_CAMPOS):
        item = app.auto_entries.get(clave)

        if not item:
            continue

        fila = i % 6
        columna = i // 6

        _crear_fila_editor(
            app.auto_edit_card,
            etiqueta,
            item["entry"],
            fila,
            columna,
            obligatorio=(clave == "serial"),
        )

    app.auto_edit_card.columnconfigure(1, weight=1)
    app.auto_edit_card.columnconfigure(3, weight=1)

    ayuda = tk.Label(
        frame,
        text="* N° de serie obligatorio. Código inventario opcional.",
        bg=C["gris_panel"],
        fg=C["rojo"],
        font=("Segoe UI", 8, "italic"),
        anchor="w",
    )
    ayuda.pack(anchor="w", padx=10, pady=(0, 4))

    app.abrir_auto_edicion = lambda: alternar_auto(app, True)

    _instalar_cierre_al_hacer_click_fuera(app)

def mostrar_discos_en_auto_frame(app) -> None:
    disco = obtener_disco_principal(app.discos_fisicos)

    texto = "—"

    if disco:
        tipo = str(disco.get("tipo", "") or "Disco").strip()
        capacidad = formatear_capacidad(str(disco.get("capacidad", "") or "").strip())

        if capacidad:
            texto = f"{tipo} {capacidad}".strip()

    item = app.auto_entries.get("disco_principal")

    if item:
        item["var"].set(texto)