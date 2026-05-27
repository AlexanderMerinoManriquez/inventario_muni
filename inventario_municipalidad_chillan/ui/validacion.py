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
        getattr(getattr(app, "buscador_departamento", None), "entry", None),
        getattr(getattr(app, "buscador_registrador", None), "entry", None),
        getattr(app, "entry_nombre_registrador", None),
    ):
        set_entry_normal(entry)

    for clave in ("serial", "codigo_inventario"):
        item = app.auto_entries.get(clave)

        if item:
            set_entry_normal(item.get("entry"))

    for lista in (app.monitores_vars, app.impresoras_vars):
        for item in lista:
            entries = item.get("entries", {})

            for clave in ("numero_de_serie", "codigo_inventario"):
                set_entry_normal(entries.get(clave))


def _primer_equipo(payload: dict) -> dict:
    equipos = payload.get("equipos") or []

    if not equipos:
        return {}

    return equipos[0] or {}


def marcar_validacion_visual(app, payload: dict) -> None:
    asignacion = payload.get("asignacion") or {}
    equipo = _primer_equipo(payload)

    if not asignacion.get("id_funcionario"):
        set_entry_error(app, getattr(app.buscador_funcionario, "entry", None))
        set_entry_error(app, getattr(app, "entry_rut_funcionario", None))

    if not asignacion.get("id_departamento"):
        set_entry_error(app, getattr(app.buscador_departamento, "entry", None))

    if not asignacion.get("id_registrador"):
        set_entry_error(app, getattr(app.buscador_registrador, "entry", None))
        set_entry_error(app, getattr(app, "entry_nombre_registrador", None))

    if not (
        equipo.get("numero_de_serie")
        or equipo.get("codigo_inventario")
    ):
        for clave in ("serial", "codigo_inventario"):
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