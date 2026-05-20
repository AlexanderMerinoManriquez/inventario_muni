import requests


def leer_url_api(config_path: str) -> tuple[str | None, str | None]:
    try:
        with open(config_path, encoding="utf-8") as archivo:
            url = archivo.read().strip()

    except Exception as e:
        return None, f"No se encontró config.txt\n\n{e}"

    if not url:
        return None, "config.txt está vacío. Debes configurar la URL de la API antes de registrar."

    return url, None


def enviar_payload_api(url: str, payload: dict) -> dict:
    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=30,
        )

    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "tipo": "conexion",
            "mensaje": str(e),
            "detalle": str(e),
        }

    try:
        data = resp.json()
    except Exception:
        return {
            "ok": False,
            "tipo": "respuesta_no_json",
            "mensaje": "El servidor no devolvió JSON válido.",
            "detalle": resp.text,
        }

    if data.get("success") is True:
        return {
            "ok": True,
            "data": data,
        }

    return {
        "ok": False,
        "tipo": "servidor",
        "mensaje": data.get("message", "Sin mensaje"),
        "detalle": resp.text,
        "data": data,
    }