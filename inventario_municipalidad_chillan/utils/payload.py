import re
from datetime import datetime
 
from config import OBLIGATORIOS
 
def limpiar_var(var) -> str:
    return var.get().strip().lower()

def normalizar_ram_gb(valor) -> float | None:
    texto = str(valor or "").upper().replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", texto)

    if not match:
        return None

    ram = float(match.group())

    valores_ram = [2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 256]

    return float(min(valores_ram, key=lambda x: abs(x - ram)))
 
 
def _capacidad_numero(disco: dict) -> float:
    capacidad = str(disco.get("capacidad", "") or "").upper().replace("GB", "").strip()
    try:
        return float(capacidad)
    except ValueError:
        return 0
 
 
def _ordenar_discos(discos: list[dict]) -> list[dict]:
    """SSD primero, luego por capacidad descendente."""
    return sorted(
        discos,
        key=lambda d: (str(d.get("tipo", "")).upper() != "SSD", -_capacidad_numero(d)),
    )
 
 
def _separar_disco_principal(discos: list[dict]) -> tuple[dict | None, list[dict]]:
    if not discos:
        return None, []
    ordenados = _ordenar_discos(discos)
    return ordenados[0], ordenados[1:]
 
 
def _observacion_discos_secundarios(discos: list[dict]) -> str | None:
    if not discos:
        return None
 
    partes = []
    for disco in discos:
        tipo = str(disco.get("tipo", "disco") or "disco").upper()
        capacidad = str(disco.get("capacidad", "") or "").strip()
        sufijo = f" de capacidad {capacidad}" if capacidad else ""
        partes.append(f"Este equipo cuenta con otro disco de almacenamiento {tipo}{sufijo}.")
 
    return " ".join(partes)
 
 
def construir_payload(app) -> dict:
    monitores = [
        {k: item[k].get().strip().lower() for k in ("marca", "modelo", "pulgadas")}
        for item in app.monitores_vars
    ]
    impresoras = []

    for item in app.impresoras_vars:
        impresora = {
            k: item[k].get().strip().lower()
            for k in ("tipo", "marca", "modelo", "ip", "toner_tinta")
        }
        tiene_datos = any(impresora.values())

        if not tiene_datos:
            continue
        
        es_no_detectada = impresora.get("tipo") == "no detectada"
        tiene_datos_reales = any(
            impresora.get(campo)
            for campo in ("marca", "modelo", "ip", "toner_tinta")
        )
        if es_no_detectada and not tiene_datos_reales:
            continue

        impresoras.append(impresora)

    disco_principal, discos_secundarios = _separar_disco_principal(app.discos_fisicos)

    obs_usuario = app.txt_observaciones.get("1.0", "end").strip()
    obs_discos  = _observacion_discos_secundarios(discos_secundarios)
    observaciones = " ".join(p for p in (obs_usuario, obs_discos) if p).strip() or None

    auto = {c: app._get_auto(c) for c, _ in app.AUTO_FIELDS}
    ram_original = auto.pop("ram", None)

    return {
        **auto,

        "ram_gb": normalizar_ram_gb(ram_original),

        "nombre_funcionario":   limpiar_var(app.var_usuario),
        "rut_funcionario":      limpiar_var(app.var_rut_funcionario),

        "registrado_por":       limpiar_var(app.var_registrado_por),
        "rut_registrado_por":   limpiar_var(app.var_rut_registrado_por),

        "fecha_hora_registro":  app.fecha_hora_envio or datetime.now().strftime("%Y-%m-%d %H:%M"),

        "tipo_disco":           str((disco_principal or {}).get("tipo", "")).lower() or None,
        "capacidad_disco":      str((disco_principal or {}).get("capacidad", "")).lower() or None,

        "codigo_inventario":    None,
        "departamento_manual":  limpiar_var(app.var_departamento_manual),
        "monitores":            monitores,
        "impresoras":           impresoras,
        "observaciones":        observaciones.lower() if observaciones else None,
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