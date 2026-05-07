from funciones.tipo_equipo import texto_tipo_equipo_integrado
from utils.discos_modelo import obtener_discos_secundarios


def agregar_observacion_automatica(app, texto: str) -> None:
    if not hasattr(app, "txt_observaciones"):
        return

    texto = str(texto or "").strip()

    if not texto:
        return

    if not texto.startswith("•"):
        texto = f"• {texto}"

    texto_actual = app.txt_observaciones.get("1.0", "end").strip()

    if texto.lower() in texto_actual.lower():
        return

    if texto_actual:
        app.txt_observaciones.insert("end", "\n\n" + texto)
    else:
        app.txt_observaciones.insert("1.0", texto)


def agregar_observacion_pantallas_integradas(app, monitores: list[dict]) -> None:
    if not monitores:
        return

    detalles = []

    for monitor in monitores:
        partes = []

        marca = str(monitor.get("marca") or "").strip()
        modelo = str(monitor.get("modelo") or "").strip()
        pulgadas = str(monitor.get("pulgadas") or "").strip()
        serial = str(monitor.get("numero_de_serie") or "").strip()

        if marca:
            partes.append(f"marca {marca}")

        if modelo:
            partes.append(f"modelo {modelo}")

        if pulgadas:
            partes.append(f"{pulgadas} pulgadas")

        if serial:
            partes.append(f"N° serie {serial}")

        if partes:
            detalles.append("(" + ", ".join(partes) + ")")

    tipo_integrado = texto_tipo_equipo_integrado(app.tipo_equipo_fisico)

    if len(monitores) == 1:
        texto = f"Se detectó una pantalla integrada {tipo_integrado}"

        if detalles:
            texto += f" {detalles[0]}"

        texto += "; no se registra como monitor independiente."
    else:
        texto = f"Se detectaron {len(monitores)} pantallas integradas {tipo_integrado}"

        if detalles:
            texto += ": " + "; ".join(detalles)

        texto += ". No se registran como monitores independientes."

    agregar_observacion_automatica(app, texto)


def agregar_observacion_discos_secundarios(app) -> None:
    textos = []

    for disco in obtener_discos_secundarios(app.discos_fisicos):
        tipo = str(disco.get("tipo", "disco") or "disco").upper()
        capacidad = str(disco.get("capacidad", "") or "").strip()

        if capacidad:
            textos.append(
                f"Este equipo cuenta con otro disco de almacenamiento {tipo} de capacidad {capacidad}."
            )
        else:
            textos.append(
                f"Este equipo cuenta con otro disco de almacenamiento {tipo}."
            )

    if textos:
        agregar_observacion_automatica(app, " ".join(textos))