import html
import json

from config import (
    API_FUNCIONARIOS_URL,
    API_USUARIOS_SISTEMA_URL,
    API_SOURCE_FUNCIONARIOS,
    API_SOURCE_USUARIOS_SISTEMA,
)
from utils.api_datos import consultar_api_get
from utils.rut import formatear_rut


def _texto(valor) -> str:
    return html.unescape(str(valor or "").strip())


def _normalizar_persona(item: dict) -> dict | None:
    rut = formatear_rut(item.get("rut", "")) or ""
    nombre = _texto(item.get("nombre"))

    if not rut and not nombre:
        return None

    return {
        "rut": rut,
        "nombre": nombre,
    }


def _cargar_personas_api(url: str, source: str) -> list[dict]:
    personas = []

    for item in consultar_api_get(url, source=source):
        if not isinstance(item, dict):
            continue

        persona = _normalizar_persona(item)

        if persona:
            personas.append(persona)

    return personas


def cargar_funcionarios():
    return _cargar_personas_api(
        API_FUNCIONARIOS_URL,
        API_SOURCE_FUNCIONARIOS,
    )


def cargar_usuarios_sistema():
    return _cargar_personas_api(
        API_USUARIOS_SISTEMA_URL,
        API_SOURCE_USUARIOS_SISTEMA,
    )


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