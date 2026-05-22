import re
from datetime import datetime

from utils.discos_modelo import extraer_capacidad_gb, separar_disco_principal
from utils.rut import formatear_rut, validar_rut
from utils.serial_utils import normalizar_serial


def limpiar_texto(valor) -> str | None:
    texto = str(valor or "").strip()
    return texto or None


def limpiar_var(var) -> str | None:
    return limpiar_texto(var.get())


def normalizar_codigo_inventario(valor) -> str | None:
    texto = str(valor or "").strip().upper()
    return texto or None


def normalizar_identificador(valor) -> str | None:
    return normalizar_serial(valor, min_len=3)


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


def _limpiar_items(vars_lista: list[dict], campos: tuple[str, ...]) -> list[dict]:
    items = []

    for item in vars_lista:
        fila = {}

        for campo in campos:
            var = item.get(campo)
            valor = limpiar_texto(var.get()) if var else None

            if campo == "codigo_inventario":
                valor = normalizar_codigo_inventario(valor)

            elif campo == "numero_de_serie":
                valor = normalizar_identificador(valor)

            elif campo == "pulgadas":
                valor = extraer_numero_decimal(valor)

            fila[campo] = valor

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
            for campo in (
                "marca",
                "modelo",
                "ip",
                "toner_tinta",
                "codigo_inventario",
                "numero_de_serie",
            )
        )

        if es_no_detectada and not tiene_datos_reales:
            continue

        resultado.append({
            "tipo_impresora": impresora.get("tipo"),
            "marca": impresora.get("marca"),
            "modelo": impresora.get("modelo"),
            "ip": impresora.get("ip"),
            "toner_tinta": impresora.get("toner_tinta"),
            "numero_de_serie": impresora.get("numero_de_serie"),
            "codigo_inventario": impresora.get("codigo_inventario"),
        })

    return resultado


def _tiene_identificador(item: dict) -> bool:
    return bool(
        item.get("codigo_inventario")
        or item.get("numero_de_serie")
    )


def construir_payload(app) -> dict:
    auto = {
        clave: limpiar_texto(app._get_auto(clave))
        for clave, _ in app.AUTO_FIELDS
    }

    disco_principal, _ = separar_disco_principal(app.discos_fisicos)

    monitores = _limpiar_items(
        app.monitores_vars,
        (
            "marca",
            "modelo",
            "pulgadas",
            "numero_de_serie",
            "codigo_inventario",
        ),
    )

    impresoras_raw = _limpiar_items(
        app.impresoras_vars,
        (
            "tipo",
            "marca",
            "modelo",
            "ip",
            "toner_tinta",
            "numero_de_serie",
            "codigo_inventario",
        ),
    )

    impresoras = _limpiar_impresoras(impresoras_raw)

    observaciones = app.txt_observaciones.get("1.0", "end").strip() or None

    return {
        "codigo_inventario_equipo": normalizar_codigo_inventario(
            app._get_auto("codigo_inventario_equipo")
        ),
        "numero_de_serie_equipo": normalizar_identificador(auto.get("serial")),

        "nombre_pc": auto.get("nombre_pc"),
        "sistema_operativo": auto.get("sistema_operativo"),
        "procesador": auto.get("cpu"),
        "ram_gb": normalizar_ram_gb(auto.get("ram")),

        "tipo_disco_principal": limpiar_texto(
            str((disco_principal or {}).get("tipo", "")).upper()
        ),
        "capacidad_disco_principal_gb": extraer_capacidad_gb(
            (disco_principal or {}).get("capacidad")
        ),

        "ip": auto.get("ip"),
        "anydesk": auto.get("anydesk"),

        "nombre_funcionario": limpiar_var(app.var_usuario),
        "rut_funcionario": formatear_rut(limpiar_var(app.var_rut_funcionario)),
        "departamento_funcionario": limpiar_var(app.var_departamento_funcionario),

        "nombre_registrador": limpiar_var(app.var_nombre_registrador),
        "rut_registrador": formatear_rut(limpiar_var(app.var_rut_registrador)),

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
        "rut_funcionario": "RUT funcionario",
        "departamento_funcionario": "Departamento",
        "nombre_registrador": "Nombre registrador",
        "rut_registrador": "RUT registrador",
        "fecha_hora_registro": "Fecha y hora",
    }

    faltantes = []

    for clave, nombre_visible in obligatorios.items():
        valor = payload.get(clave)

        if valor is None or valor == "":
            faltantes.append(nombre_visible)
            
    if payload.get("rut_funcionario") and not validar_rut(payload.get("rut_funcionario")):
        faltantes.append("RUT funcionario válido")

    if payload.get("rut_registrador") and not validar_rut(payload.get("rut_registrador")):
        faltantes.append("RUT registrador válido")

    if not (
        payload.get("codigo_inventario_equipo")
        or payload.get("numero_de_serie_equipo")
    ):
        faltantes.append("Equipo: código inventario o N° serie")

    for i, monitor in enumerate(payload.get("monitores") or [], start=1):
        if not _tiene_identificador(monitor):
            faltantes.append(f"Monitor {i}: código inventario o N° serie")

    for i, impresora in enumerate(payload.get("impresoras") or [], start=1):
        if not _tiene_identificador(impresora):
            faltantes.append(f"Impresora {i}: código inventario o N° serie")

    return not faltantes, faltantes