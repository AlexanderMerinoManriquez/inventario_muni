import json
import subprocess


CHASSIS_NOTEBOOK = {
    8,   # Portable
    9,   # Laptop
    10,  # Notebook
    14,  # Sub Notebook
    30,  # Tablet
    31,  # Convertible
    32,  # Detachable
}

CHASSIS_ALL_IN_ONE = {
    13,  # All in One
}

PALABRAS_NOTEBOOK = (
    "laptop",
    "notebook",
    "thinkpad",
    "ideapad",
    "vivobook",
    "zenbook",
    "latitude",
    "inspiron",
    "elitebook",
    "probook",
    "pavilion",
    "aspire",
    "travelmate",
)

PALABRAS_ALL_IN_ONE = (
    "all in one",
    "all-in-one",
    "aio",
    "ideacentre",
    "thinkcentre aio",
    "optiplex aio",
    "proone",
    "eliteone",
)


def _normalizar_texto(valor) -> str:
    return str(valor or "").strip().lower()


def _obtener_chassis(chassis) -> list[int]:
    if chassis is None:
        return []

    if isinstance(chassis, int):
        return [chassis]

    if isinstance(chassis, list):
        resultado = []

        for item in chassis:
            try:
                resultado.append(int(item))
            except (TypeError, ValueError):
                continue

        return resultado

    try:
        return [int(chassis)]
    except (TypeError, ValueError):
        return []


def detectar_tipo_equipo() -> str:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$enclosure = Get-CimInstance Win32_SystemEnclosure |
    Select-Object Manufacturer, Model, ChassisTypes

$system = Get-CimInstance Win32_ComputerSystem |
    Select-Object Manufacturer, Model, PCSystemType, PCSystemTypeEx

[PSCustomObject]@{
    Enclosure = $enclosure
    System = $system
} | ConvertTo-Json -Depth 5 -Compress
"""

    try:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        if proc.returncode != 0 or not proc.stdout.strip():
            return "DESCONOCIDO"

        data = json.loads(proc.stdout.strip())

        enclosure = data.get("Enclosure") or {}
        system = data.get("System") or {}

        chassis = _obtener_chassis(enclosure.get("ChassisTypes"))

        if any(c in CHASSIS_NOTEBOOK for c in chassis):
            return "NOTEBOOK"

        if any(c in CHASSIS_ALL_IN_ONE for c in chassis):
            return "ALL_IN_ONE"

        texto_modelo = " ".join([
            str(system.get("Manufacturer") or ""),
            str(system.get("Model") or ""),
            str(enclosure.get("Manufacturer") or ""),
            str(enclosure.get("Model") or ""),
        ])

        texto_modelo = _normalizar_texto(texto_modelo)

        if any(palabra in texto_modelo for palabra in PALABRAS_NOTEBOOK):
            return "NOTEBOOK"

        if any(palabra in texto_modelo for palabra in PALABRAS_ALL_IN_ONE):
            return "ALL_IN_ONE"

        if chassis:
            return "DESKTOP"

        return "DESCONOCIDO"

    except Exception:
        return "DESCONOCIDO"


def texto_tipo_equipo_integrado(tipo: str) -> str:
    tipo = str(tipo or "").upper().strip()

    if tipo == "NOTEBOOK":
        return "de un notebook/laptop"

    if tipo == "ALL_IN_ONE":
        return "de un equipo All in One"

    return "del equipo"