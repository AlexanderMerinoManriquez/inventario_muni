import html

from config import (
    API_FUNCIONARIOS_URL,
    API_USUARIOS_SISTEMA_URL,
    API_DEPARTAMENTOS_URL,
    API_SOURCE_FUNCIONARIOS,
    API_SOURCE_USUARIOS_SISTEMA,
    API_SOURCE_DEPARTAMENTOS,
)
from utils.api_datos import consultar_api_get
from utils.rut import formatear_rut


def _texto(valor) -> str:
    return html.unescape(str(valor or "").strip())


def _normalizar_id(valor):
    try:
        if valor is None or str(valor).strip() == "":
            return None

        return int(valor)

    except (TypeError, ValueError):
        return None


def _normalizar_persona(item: dict) -> dict | None:
    id_persona = _normalizar_id(
        item.get("id")
        or item.get("id_funcionario")
        or item.get("id_usuario")
    )

    rut = formatear_rut(item.get("rut", "")) or ""
    nombre = _texto(item.get("nombre"))

    if id_persona is None or not nombre:
        return None

    return {
        "id": id_persona,
        "rut": rut,
        "nombre": nombre,
    }


def _normalizar_departamento(item: dict) -> dict | None:
    id_departamento = _normalizar_id(
        item.get("id")
        or item.get("id_departamento")
        or item.get("departamento_id")
    )

    nombre = _texto(
        item.get("nombre")
        or item.get("nombre_departamento")
        or item.get("departamento")
    )

    if id_departamento is None or not nombre:
        return None

    return {
        "id": id_departamento,
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


def cargar_departamentos():
    departamentos = []

    if not API_DEPARTAMENTOS_URL:
        return departamentos

    for item in consultar_api_get(API_DEPARTAMENTOS_URL, source=API_SOURCE_DEPARTAMENTOS):
        if not isinstance(item, dict):
            continue

        departamento = _normalizar_departamento(item)

        if departamento:
            departamentos.append(departamento)

    return departamentos