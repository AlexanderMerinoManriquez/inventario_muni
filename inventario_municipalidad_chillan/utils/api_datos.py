import requests

from config import API_DATOS_TIMEOUT


def consultar_api_get(url: str) -> list:
    if not url:
        return []

    try:
        resp = requests.get(
            url,
            timeout=API_DATOS_TIMEOUT,
        )
        resp.raise_for_status()

    except requests.exceptions.RequestException:
        return []

    try:
        data = resp.json()
    except Exception:
        return []

    return extraer_lista_respuesta(data)


def extraer_lista_respuesta(data) -> list:
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for clave in ("data", "datos", "funcionarios", "usuarios", "results", "items"):
        valor = data.get(clave)

        if isinstance(valor, list):
            return valor

    return []
