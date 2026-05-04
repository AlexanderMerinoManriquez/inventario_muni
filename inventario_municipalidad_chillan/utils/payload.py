from datetime import datetime

from config import OBLIGATORIOS


def limpiar_var(var) -> str:
    return var.get().strip().lower()


def _capacidad_numero(disco: dict) -> float:
    capacidad = str(disco.get("capacidad", "") or "")
    capacidad = capacidad.upper().replace("GB", "").strip()

    try:
        return float(capacidad)
    except ValueError:
        return 0


def _separar_disco_principal(discos: list[dict]) -> tuple[dict | None, list[dict]]:
    if not discos:
        return None, []

    discos_ordenados = sorted(
        discos,
        key=lambda d: (
            str(d.get("tipo", "")).upper() != "SSD",
            -_capacidad_numero(d),
        ),
    )

    principal = discos_ordenados[0]
    secundarios = discos_ordenados[1:]

    return principal, secundarios


def _observacion_discos_secundarios(discos: list[dict]) -> str | None:
    if not discos:
        return None

    partes = []

    for disco in discos:
        tipo = str(disco.get("tipo", "disco") or "disco").upper()
        capacidad = str(disco.get("capacidad", "") or "").strip()

        if capacidad:
            partes.append(
                f"Este equipo cuenta con otro disco de almacenamiento {tipo} de capacidad {capacidad}."
            )
        else:
            partes.append(
                f"Este equipo cuenta con otro disco de almacenamiento {tipo}."
            )

    return " ".join(partes)


def construir_payload(app) -> dict:
    monitores = [
        {k: item[k].get().strip().lower() for k in ("marca", "modelo", "pulgadas")}
        for item in app.monitores_vars
    ]

    impresoras = [
        {k: item[k].get().strip().lower() for k in ("tipo", "marca", "modelo", "ip", "toner_tinta")}
        for item in app.impresoras_vars
    ]

    disco_principal, discos_secundarios = _separar_disco_principal(app.discos_fisicos)

    observaciones_usuario = app.txt_observaciones.get("1.0", "end").strip()
    observaciones_discos = _observacion_discos_secundarios(discos_secundarios)

    observaciones = " ".join(
        parte for parte in (observaciones_usuario, observaciones_discos)
        if parte
    ).strip() or None

    return {
        **{c: app._get_auto(c) for c, _ in app.AUTO_FIELDS},

        "nombre_funcionario": limpiar_var(app.var_usuario),
        "rut_funcionario": limpiar_var(app.var_rut_funcionario),

        "registrado_por": limpiar_var(app.var_registrado_por),
        "rut_registrado_por": limpiar_var(app.var_rut_registrado_por),

        "fecha_hora_registro": app.fecha_hora_envio or datetime.now().strftime("%Y-%m-%d %H:%M"),

        "tipo_disco": str((disco_principal or {}).get("tipo", "")).lower() or None,
        "capacidad_disco": str((disco_principal or {}).get("capacidad", "")).lower() or None,

        "codigo_inventario": None,
        "departamento_manual": limpiar_var(app.var_departamento_manual),
        "monitores": monitores,
        "impresoras": impresoras,
        "observaciones": observaciones.lower() if observaciones else None,
    }


def validar_payload(payload: dict) -> tuple[bool, list[str]]:
    faltantes = [
        nombre for clave, nombre in OBLIGATORIOS.items()
        if not payload.get(clave)
    ]

    if not payload.get("rut_funcionario"):
        faltantes.append("Funcionario válido desde lista")

    if not payload.get("rut_registrado_por"):
        faltantes.append("Registrador válido desde lista")

    if not payload.get("fecha_hora_registro"):
        faltantes.append("Fecha y hora")

    return not faltantes, faltantes