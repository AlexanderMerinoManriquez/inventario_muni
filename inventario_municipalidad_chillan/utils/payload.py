import re
from datetime import datetime

from utils.discos_modelo import extraer_capacidad_gb, separar_disco_principal
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


def normalizar_id(valor) -> int | None:
    try:
        if valor is None or str(valor).strip() == "":
            return None

        return int(valor)

    except (TypeError, ValueError):
        return None


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


def _primer_equipo(payload: dict) -> dict:
    equipos = payload.get("equipos") or []

    if not equipos:
        return {}

    return equipos[0] or {}


def construir_payload(app) -> dict:
    auto = {
        clave: limpiar_texto(app._get_auto(clave))
        for clave, _ in app.AUTO_FIELDS
    }

    disco_principal, _ = separar_disco_principal(app.discos_fisicos)

    equipo = {
        "codigo_inventario": normalizar_codigo_inventario(
            app._get_auto("codigo_inventario")
        ),
        "numero_de_serie": normalizar_identificador(auto.get("serial")),
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
    }

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

    fecha_hora_registro = (
        app.fecha_hora_envio
        or datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    observaciones = app.txt_observaciones.get("1.0", "end").strip() or None

    id_funcionario = normalizar_id(
        getattr(app, "id_funcionario_seleccionado", None)
    )

    id_departamento = normalizar_id(
        getattr(app, "id_departamento_seleccionado", None)
    )

    id_registrador = normalizar_id(
        getattr(app, "id_registrador_seleccionado", None)
    )

    return {
        "equipos": [equipo],
        "monitores": monitores,
        "impresoras": impresoras,

        "asignacion": {
            "id_funcionario": id_funcionario,
            "id_departamento": id_departamento,

            # Se envían ambos por compatibilidad con backend.
            # En la BD real corresponde a asignaciones_activo.asignado_por.
            "id_registrador": id_registrador,
            "asignado_por": id_registrador,

            "fecha_hora_registro": fecha_hora_registro,
            "observaciones": observaciones,
        },
    }


def validar_payload(payload: dict) -> tuple[bool, list[str]]:
    faltantes = []

    equipo = _primer_equipo(payload)
    asignacion = payload.get("asignacion") or {}

    obligatorios_equipo = {
        "nombre_pc": "Nombre del PC",
        "sistema_operativo": "Sistema operativo",
        "procesador": "Procesador",
        "ram_gb": "RAM",
    }

    for clave, nombre_visible in obligatorios_equipo.items():
        valor = equipo.get(clave)

        if valor is None or valor == "":
            faltantes.append(nombre_visible)

    obligatorios_asignacion = {
        "id_funcionario": "Funcionario seleccionado desde la lista",
        "id_departamento": "Departamento seleccionado desde la lista",
        "id_registrador": "Registrador seleccionado desde la lista",
        "fecha_hora_registro": "Fecha y hora",
    }

    for clave, nombre_visible in obligatorios_asignacion.items():
        valor = asignacion.get(clave)

        if valor is None or valor == "":
            faltantes.append(nombre_visible)

    if not _tiene_identificador(equipo):
        faltantes.append("Equipo: código inventario o N° serie")

    for i, monitor in enumerate(payload.get("monitores") or [], start=1):
        if not _tiene_identificador(monitor):
            faltantes.append(f"Monitor {i}: código inventario o N° serie")

    for i, impresora in enumerate(payload.get("impresoras") or [], start=1):
        if not _tiene_identificador(impresora):
            faltantes.append(f"Impresora {i}: código inventario o N° serie")

    return not faltantes, faltantes