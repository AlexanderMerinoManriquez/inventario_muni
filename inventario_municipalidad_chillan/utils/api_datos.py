import requests

from config import API_DATOS_TIMEOUT


def consultar_api_get(url: str, source: str | None = None) -> list:
    if not url:
        return []

    params = {}

    if source:
        params["source"] = source

    try:
        resp = requests.get(
            url,
            params=params,
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