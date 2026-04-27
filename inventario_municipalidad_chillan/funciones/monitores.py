import json
import math
import subprocess


FABRICANTES = {
    "LEN": "Lenovo",
    "GSM": "LG",
    "DEL": "Dell",
    "AUS": "ASUS",
    "ACI": "Acer",
    "SAM": "Samsung",
    "SEC": "Samsung",
    "HPN": "HP",
    "PHL": "Philips",
    "CMN": "Chi Mei",
    "AUO": "AU Optronics",
    "BOE": "BOE",
    "MSI": "MSI",
    "BNQ": "BenQ",
    "VSC": "ViewSonic",
    "APP": "Apple",
}


def _limpiar_wmi(valor):
    if not valor:
        return ""
    try:
        if isinstance(valor, list):
            return "".join(chr(int(x)) for x in valor if int(x) != 0).strip()
        return str(valor).strip()
    except Exception:
        return ""


def _normalizar_marca(codigo):
    codigo = (codigo or "").strip().upper()
    return FABRICANTES.get(codigo, codigo.title() if codigo else "")


def _normalizar_modelo(modelo):
    modelo = (modelo or "").strip()
    if not modelo:
        return ""

    upper = modelo.upper()

    if upper.startswith("LEN-"):
        return "Lenovo " + modelo[4:].strip()
    if upper.startswith("GSM"):
        resto = modelo[3:].strip(" -_")
        return f"LG {resto}".strip()
    if upper.startswith("DEL"):
        resto = modelo[3:].strip(" -_")
        return f"Dell {resto}".strip()
    if upper.startswith("AUS"):
        resto = modelo[3:].strip(" -_")
        return f"ASUS {resto}".strip()
    if upper.startswith("ACI"):
        resto = modelo[3:].strip(" -_")
        return f"Acer {resto}".strip()
    if upper.startswith("HPN"):
        resto = modelo[3:].strip(" -_")
        return f"HP {resto}".strip()
    if upper.startswith("PHL"):
        resto = modelo[3:].strip(" -_")
        return f"Philips {resto}".strip()

    return modelo


def _calcular_pulgadas(ancho_cm, alto_cm):
    try:
        ancho = float(ancho_cm)
        alto = float(alto_cm)
        if ancho <= 0 or alto <= 0:
            return ""
        diagonal_cm = math.sqrt(ancho ** 2 + alto ** 2)
        return str(int(round(diagonal_cm / 2.54)))
    except Exception:
        return ""


def obtener_monitores():
    script = r"""
$ErrorActionPreference = 'Stop'

$ids = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID
$params = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams

$resultado = @()

foreach ($m in $ids) {
    $p = $params | Where-Object { $_.InstanceName -eq $m.InstanceName } | Select-Object -First 1

    $resultado += [PSCustomObject]@{
        InstanceName = $m.InstanceName
        ManufacturerName = @($m.ManufacturerName)
        UserFriendlyName = @($m.UserFriendlyName)
        SerialNumberID = @($m.SerialNumberID)
        MaxHorizontalImageSize = if ($p) { $p.MaxHorizontalImageSize } else { 0 }
        MaxVerticalImageSize   = if ($p) { $p.MaxVerticalImageSize } else { 0 }
    }
}

$resultado | ConvertTo-Json -Depth 4 -Compress
"""

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=25,
        )

        if proc.returncode != 0:
            return []

        salida = (proc.stdout or "").strip()
        if not salida:
            return []

        data = json.loads(salida)

        if isinstance(data, dict):
            data = [data]

        monitores = []
        for item in data:
            codigo = _limpiar_wmi(item.get("ManufacturerName"))
            modelo_raw = _limpiar_wmi(item.get("UserFriendlyName"))
            serial = _limpiar_wmi(item.get("SerialNumberID"))

            monitores.append({
                "instancia": item.get("InstanceName", ""),
                "marca": _normalizar_marca(codigo),
                "modelo": _normalizar_modelo(modelo_raw),
                "serial": serial,
                "pulgadas": _calcular_pulgadas(
                    item.get("MaxHorizontalImageSize", 0),
                    item.get("MaxVerticalImageSize", 0),
                ),
            })

        return monitores

    except Exception:
        return []