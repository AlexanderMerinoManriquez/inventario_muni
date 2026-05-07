import re


def extraer_capacidad_gb(valor) -> float | None:
    texto = str(valor or "").upper().replace(",", ".").strip()
    match = re.search(r"\d+(?:\.\d+)?", texto)

    if not match:
        return None

    capacidad = float(match.group())

    if "TB" in texto and "GB" not in texto:
        return capacidad * 1024

    return capacidad


def capacidad_disco_gb(disco: dict) -> float:
    return extraer_capacidad_gb((disco or {}).get("capacidad")) or 0


def ordenar_discos(discos: list[dict] | None) -> list[dict]:
    return sorted(
        discos or [],
        key=lambda d: (
            str((d or {}).get("tipo", "")).upper() != "SSD",
            -capacidad_disco_gb(d),
        ),
    )


def obtener_disco_principal(discos: list[dict] | None) -> dict | None:
    ordenados = ordenar_discos(discos)
    return ordenados[0] if ordenados else None


def separar_disco_principal(discos: list[dict] | None) -> tuple[dict | None, list[dict]]:
    ordenados = ordenar_discos(discos)

    if not ordenados:
        return None, []

    return ordenados[0], ordenados[1:]


def obtener_discos_secundarios(discos: list[dict] | None) -> list[dict]:
    _, secundarios = separar_disco_principal(discos)
    return secundarios