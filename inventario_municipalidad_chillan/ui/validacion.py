def activar_limpieza_error_al_escribir(app, entry) -> None:
    if not entry or getattr(entry, "_limpia_error_bind", False):
        return

    def limpiar(_=None, e=entry):
        set_entry_normal(e)

    entry.bind("<KeyRelease>", limpiar, add="+")
    entry.bind("<<Paste>>", lambda _=None: app.root.after_idle(limpiar), add="+")
    entry._limpia_error_bind = True


def set_entry_error(app, entry) -> None:
    if entry:
        entry.configure(style="Error.TEntry")
        activar_limpieza_error_al_escribir(app, entry)


def set_entry_normal(entry) -> None:
    if entry:
        entry.configure(style="TEntry")


def limpiar_validacion_visual(app) -> None:
    for entry in (
        getattr(getattr(app, "buscador_funcionario", None), "entry", None),
        getattr(app, "entry_rut_funcionario", None),
        getattr(app, "entry_departamento_funcionario", None),
        getattr(getattr(app, "buscador_registrador", None), "entry", None),
        getattr(app, "entry_nombre_registrador", None),
    ):
        set_entry_normal(entry)

    for clave in ("serial", "codigo_inventario_equipo"):
        item = app.auto_entries.get(clave)

        if item:
            set_entry_normal(item.get("entry"))

    for lista in (app.monitores_vars, app.impresoras_vars):
        for item in lista:
            entries = item.get("entries", {})

            for clave in ("numero_de_serie", "codigo_inventario"):
                set_entry_normal(entries.get(clave))


def marcar_validacion_visual(app, payload: dict) -> None:
    if not app.buscador_funcionario.es_seleccion_valida():
        set_entry_error(app, app.buscador_funcionario.entry)

    if not payload.get("rut_funcionario"):
        set_entry_error(app, app.entry_rut_funcionario)

    if not payload.get("departamento_funcionario"):
        set_entry_error(app, app.entry_departamento_funcionario)

    if not app.buscador_registrador.es_seleccion_valida():
        set_entry_error(app, app.buscador_registrador.entry)

    if not payload.get("nombre_registrador"):
        set_entry_error(app, app.entry_nombre_registrador)

    if not (
        payload.get("numero_de_serie_equipo")
        or payload.get("codigo_inventario_equipo")
    ):
        for clave in ("serial", "codigo_inventario_equipo"):
            item = app.auto_entries.get(clave)

            if item:
                set_entry_error(app, item.get("entry"))

    for i, monitor in enumerate(payload.get("monitores") or []):
        if monitor.get("numero_de_serie") or monitor.get("codigo_inventario"):
            continue

        if i < len(app.monitores_vars):
            entries = app.monitores_vars[i].get("entries", {})
            set_entry_error(app, entries.get("numero_de_serie"))
            set_entry_error(app, entries.get("codigo_inventario"))

    for i, impresora in enumerate(payload.get("impresoras") or []):
        if impresora.get("numero_de_serie") or impresora.get("codigo_inventario"):
            continue

        if i < len(app.impresoras_vars):
            entries = app.impresoras_vars[i].get("entries", {})
            set_entry_error(app, entries.get("numero_de_serie"))
            set_entry_error(app, entries.get("codigo_inventario"))