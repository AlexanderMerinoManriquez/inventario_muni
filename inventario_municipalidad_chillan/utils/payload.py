import re
from datetime import datetime


def limpiar_texto(valor) -> str | None:
    texto = str(valor or "").strip()
    return texto or None


def limpiar_var(var) -> str | None:
    return limpiar_texto(var.get())


def extraer_numero_decimal(valor) -> float | None:
    texto = str(valor or "").upper().replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", texto)

    if not match:
        return None

    return float(match.group())


def normalizar_ram_gb(valor) -> float | None:
    ram = extraer_numero_decimal(valor)

    if ram is None:
        return None

    valores_ram = [2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 256]

    return float(min(valores_ram, key=lambda x: abs(x - ram)))


def _capacidad_numero(disco: dict) -> float:
    return extraer_numero_decimal(disco.get("capacidad")) or 0


def _ordenar_discos(discos: list[dict]) -> list[dict]:
    """SSD primero, luego por capacidad descendente."""
    return sorted(
        discos,
        key=lambda d: (
            str(d.get("tipo", "")).upper() != "SSD",
            -_capacidad_numero(d),
        ),
    )


def _separar_disco_principal(discos: list[dict]) -> tuple[dict | None, list[dict]]:
    if not discos:
        return None, []

    ordenados = _ordenar_discos(discos)
    return ordenados[0], ordenados[1:]


def _limpiar_items(vars_lista: list[dict], campos: tuple[str, ...]) -> list[dict]:
    items = []

    for item in vars_lista:
        fila = {}

        for campo in campos:
            var = item.get(campo)
            fila[campo] = limpiar_texto(var.get()) if var else None

        if any(fila.values()):
            items.append(fila)

    return items


def _limpiar_impresoras(impresoras: list[dict]) -> list[dict]:
    resultado = []

    for impresora in impresoras:
        tipo = (impresora.get("tipo") or "").strip().lower()

        es_no_detectada = tipo == "no detectada"
        tiene_datos_reales = any(
            impresora.get(campo)
            for campo in ("marca", "modelo", "ip", "toner_tinta")
        )

        if es_no_detectada and not tiene_datos_reales:
            continue

        resultado.append({
            "tipo_impresora": impresora.get("tipo"),
            "marca": impresora.get("marca"),
            "modelo": impresora.get("modelo"),
            "ip": impresora.get("ip"),
            "toner_tinta": impresora.get("toner_tinta"),
        })

    return resultado


def construir_payload(app) -> dict:
    auto = {
        clave: limpiar_texto(app._get_auto(clave))
        for clave, _ in app.AUTO_FIELDS
    }

    disco_principal, _ = _separar_disco_principal(app.discos_fisicos)

    monitores = _limpiar_items(
        app.monitores_vars,
        ("marca", "modelo", "pulgadas"),
    )

    impresoras_raw = _limpiar_items(
        app.impresoras_vars,
        ("tipo", "marca", "modelo", "ip", "toner_tinta"),
    )

    impresoras = _limpiar_impresoras(impresoras_raw)

    observaciones = app.txt_observaciones.get("1.0", "end").strip() or None

    return {
        "codigo_inventario": None,

        "nombre_pc": auto.get("nombre_pc"),
        "sistema_operativo": auto.get("sistema_operativo"),
        "procesador": auto.get("cpu"),
        "ram_gb": normalizar_ram_gb(auto.get("ram")),

        "tipo_disco_principal": limpiar_texto(
            str((disco_principal or {}).get("tipo", "")).upper()
        ),
        "capacidad_disco_principal_gb": extraer_numero_decimal(
            (disco_principal or {}).get("capacidad")
        ),

        "ip": auto.get("ip"),
        "anydesk": auto.get("anydesk"),
        "numero_de_serie": auto.get("serial"),

        "nombre_funcionario": limpiar_var(app.var_usuario),
        "rut_funcionario": limpiar_var(app.var_rut_funcionario),
        "departamento_manual": limpiar_var(app.var_departamento_manual),

        "registrado_por": limpiar_var(app.var_registrado_por),
        "rut_registrado_por": limpiar_var(app.var_rut_registrado_por),

        "fecha_hora_registro": (
            app.fecha_hora_envio
            or datetime.now().strftime("%Y-%m-%d %H:%M")
        ),

        "monitores": monitores,
        "impresoras": impresoras,
        "observaciones": observaciones,
    }


def validar_payload(payload: dict) -> tuple[bool, list[str]]:
    obligatorios = {
        "nombre_pc": "Nombre del PC",
        "sistema_operativo": "Sistema operativo",
        "procesador": "Procesador",
        "ram_gb": "RAM",
        "nombre_funcionario": "Funcionario responsable",
        "rut_funcionario": "Funcionario válido desde lista",
        "departamento_manual": "Departamento",
        "registrado_por": "Registrado por",
        "rut_registrado_por": "Registrador válido desde lista",
        "fecha_hora_registro": "Fecha y hora",
    }

    faltantes = []

    for clave, nombre_visible in obligatorios.items():
        valor = payload.get(clave)

        if valor is None or valor == "":
            faltantes.append(nombre_visible)

    return not faltantes, faltantes