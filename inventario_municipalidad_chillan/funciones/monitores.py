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


SERIALES_INVALIDOS = {
    "",
    "0",
    "00",
    "000",
    "0000",
    "00000",
    "000000",
    "0000000",
    "00000000",
    "NONE",
    "UNKNOWN",
    "DESCONOCIDO",
    "NO DETECTADO",
    "SIN SERIAL",
    "SIN_SERIE",
    "N/A",
    "NA",
}


VIDEO_OUTPUT = {
    -2: "No inicializado",
    -1: "Otro",
    0: "VGA",
    1: "S-Video",
    2: "Video compuesto",
    3: "Video componente",
    4: "DVI",
    5: "HDMI",
    6: "LVDS",
    8: "D-JPN",
    9: "SDI",
    10: "DisplayPort",
    11: "DisplayPort integrado",
    12: "UDI externo",
    13: "UDI integrado",
    14: "Dongle SDTV",
    15: "Miracast",
    16: "Indirect wired",
    2147483648: "Interno",
    -2147483648: "Interno",
}


VIDEO_OUTPUT_INTEGRADO = {
    6,            # LVDS
    11,           # DisplayPort integrado / eDP
    13,           # UDI integrado
    2147483648,   # Internal
    -2147483648,  # Internal como entero con signo
}


def _limpiar_wmi(valor):
    if not valor:
        return ""

    try:
        if isinstance(valor, list):
            return "".join(
                chr(int(x))
                for x in valor
                if int(x) != 0
            ).strip()

        return str(valor).strip()

    except Exception:
        return ""


def _normalizar_serial(valor: str) -> str:
    serial = str(valor or "").strip().upper()

    if serial in SERIALES_INVALIDOS:
        return ""

    if len(serial) < 3:
        return ""

    return serial


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


def _normalizar_video_output(valor) -> int | None:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _nombre_conexion(valor) -> str:
    codigo = _normalizar_video_output(valor)

    if codigo is None:
        return ""

    return VIDEO_OUTPUT.get(codigo, f"Desconocido ({codigo})")


def _es_pantalla_integrada(valor) -> bool:
    codigo = _normalizar_video_output(valor)

    if codigo is None:
        return False

    return codigo in VIDEO_OUTPUT_INTEGRADO


def obtener_monitores():
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'

$ids = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID
$params = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams
$conexiones = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorConnectionParams

$resultado = @()

foreach ($m in $ids) {
    $p = $params | Where-Object { $_.InstanceName -eq $m.InstanceName } | Select-Object -First 1
    $c = $conexiones | Where-Object { $_.InstanceName -eq $m.InstanceName } | Select-Object -First 1

    $resultado += [PSCustomObject]@{
        InstanceName = $m.InstanceName
        ManufacturerName = @($m.ManufacturerName)
        UserFriendlyName = @($m.UserFriendlyName)
        SerialNumberID = @($m.SerialNumberID)
        MaxHorizontalImageSize = if ($p) { $p.MaxHorizontalImageSize } else { 0 }
        MaxVerticalImageSize   = if ($p) { $p.MaxVerticalImageSize } else { 0 }
        VideoOutputTechnology  = if ($c) { $c.VideoOutputTechnology } else { $null }
    }
}

$resultado | ConvertTo-Json -Depth 4 -Compress
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
            serial_raw = _limpiar_wmi(item.get("SerialNumberID"))
            video_output = item.get("VideoOutputTechnology")

            monitores.append({
                "instancia": item.get("InstanceName", ""),
                "marca": _normalizar_marca(codigo),
                "modelo": _normalizar_modelo(modelo_raw),
                "pulgadas": _calcular_pulgadas(
                    item.get("MaxHorizontalImageSize", 0),
                    item.get("MaxVerticalImageSize", 0),
                ),
                "numero_de_serie": _normalizar_serial(serial_raw),
                "conexion": _nombre_conexion(video_output),
                "es_pantalla_integrada": _es_pantalla_integrada(video_output),
            })

        return monitores

    except Exception:
        return []