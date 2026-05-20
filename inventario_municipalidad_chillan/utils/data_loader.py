import json

from config import (
    API_FUNCIONARIOS_URL,
    API_USUARIOS_SISTEMA_URL,
)
from utils.api_datos import consultar_api_get
from utils.rut import formatear_rut


def _texto(valor) -> str:
    return str(valor or "").strip()


def _obtener(item: dict, *claves: str) -> str:
    for clave in claves:
        valor = item.get(clave)

        if valor is not None and str(valor).strip():
            return str(valor).strip()

    return ""


def _construir_nombre_persona(item: dict) -> str:
    nombre_completo = _obtener(
        item,
        "nombre_completo",
        "nombreCompleto",
        "funcionario",
        "usuario",
    )

    if nombre_completo:
        return nombre_completo

    nombres = _obtener(item, "nombres", "nombre")
    apellido_paterno = _obtener(
        item,
        "apellido_paterno",
        "apellidoPaterno",
        "apellidopaterno",
    )
    apellido_materno = _obtener(
        item,
        "apellido_materno",
        "apellidoMaterno",
        "apellidomaterno",
    )

    partes = [
        nombres,
        apellido_paterno,
        apellido_materno,
    ]

    return " ".join(parte for parte in partes if parte).strip()


def _normalizar_persona(item: dict) -> dict | None:
    rut = formatear_rut(
        _obtener(item, "rut", "run", "RUT", "RUN")
    ) or ""

    nombre = _construir_nombre_persona(item)

    if not rut and not nombre:
        return None

    return {
        "rut": rut,
        "nombre": nombre,
    }


def _cargar_personas_api(url: str) -> list[dict]:
    personas = []

    for item in consultar_api_get(url):
        if not isinstance(item, dict):
            continue

        persona = _normalizar_persona(item)

        if persona:
            personas.append(persona)

    return personas


def cargar_funcionarios():
    return _cargar_personas_api(API_FUNCIONARIOS_URL)


def cargar_usuarios_sistema():
    return _cargar_personas_api(API_USUARIOS_SISTEMA_URL)


def cargar_departamentos(path="data/departamentos.json"):
    departamentos = []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

            for item in data:
                nombre = ""

                if isinstance(item, dict):
                    nombre = _texto(item.get("nombre"))
                else:
                    nombre = _texto(item)

                if nombre:
                    departamentos.append({
                        "nombre": nombre
                    })

    except Exception:
        pass

    return departamentos