from datetime import datetime

from config import OBLIGATORIOS


def limpiar_var(var) -> str:
    return var.get().strip().lower()


def construir_payload(app) -> dict:
    monitores = [
        {k: item[k].get().strip().lower() for k in ("marca", "modelo", "pulgadas")}
        for item in app.monitores_vars
    ]

    impresoras = [
        {k: item[k].get().strip().lower() for k in ("tipo", "marca", "modelo", "ip", "toner_tinta")}
        for item in app.impresoras_vars
    ]

    return {
        **{c: app._get_auto(c) for c, _ in app.AUTO_FIELDS},
        "usuario": limpiar_var(app.var_usuario),
        "registrado_por": limpiar_var(app.var_registrado_por),
        "fecha_hora_registro": app.fecha_hora_envio or datetime.now().strftime("%Y-%m-%d %H:%M"),
        "discos": app.discos_fisicos,
        "codigo_inventario": None,
        "ubicacion": limpiar_var(app.var_ubicacion),
        "departamento_manual": limpiar_var(app.var_departamento_manual),
        "monitores": monitores,
        "impresoras": impresoras,
        "observaciones": app.txt_observaciones.get("1.0", "end").strip().lower() or None,
    }


def validar_payload(payload: dict) -> tuple[bool, list[str]]:
    faltantes = [
        nombre for clave, nombre in OBLIGATORIOS.items()
        if not payload.get(clave)
    ]

    if not payload.get("fecha_hora_registro"):
        faltantes.append("Fecha y hora")

    return not faltantes, faltantes