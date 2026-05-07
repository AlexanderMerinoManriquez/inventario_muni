import json
import re
import subprocess


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
    "NULL",
    "DEFAULT STRING",
    "DEFAULTSTRING",
    "SYSTEM SERIAL NUMBER",
    "SERIAL NUMBER",
    "TO BE FILLED BY O.E.M.",
    "TO BE FILLED BY OEM",
    "TOBEFILLEDBYO.E.M.",
    "TOBEFILLEDBYOEM",
    "NOT APPLICABLE",
    "NOTAPPLICABLE",
    "OEM",
    "O.E.M.",
}


def _normalizar_texto(valor) -> str:
    return str(valor or "").strip()


def _es_guid(valor: str) -> bool:
    return bool(
        re.fullmatch(
            r"\{?[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}?",
            str(valor or "").strip().upper(),
        )
    )


def _normalizar_serial(valor) -> str:
    serial = _normalizar_texto(valor).upper().strip("{}")

    if not serial:
        return ""

    serial_compacto = re.sub(r"[\s\-_\.]+", "", serial)

    if serial in SERIALES_INVALIDOS or serial_compacto in SERIALES_INVALIDOS:
        return ""

    if len(serial_compacto) < 5:
        return ""

    if _es_guid(serial):
        return ""

    if "\\" in serial or "/" in serial:
        return ""

    if "&" in serial:
        return ""

    if re.fullmatch(r"F+", serial_compacto):
        return ""

    if re.fullmatch(r"0+", serial_compacto):
        return ""

    if re.fullmatch(r"X+", serial_compacto):
        return ""

    return serial


def _extraer_valores(data) -> list[tuple[str, str]]:
    valores = []

    bios = data.get("Bios") or {}
    producto = data.get("Product") or {}
    enclosure = data.get("Enclosure") or {}
    baseboard = data.get("BaseBoard") or {}

    if isinstance(bios, list):
        bios = bios[0] if bios else {}

    if isinstance(producto, list):
        producto = producto[0] if producto else {}

    if isinstance(enclosure, list):
        enclosure = enclosure[0] if enclosure else {}

    if isinstance(baseboard, list):
        baseboard = baseboard[0] if baseboard else {}

    valores.append(("BIOS", bios.get("SerialNumber")))
    valores.append(("ComputerSystemProduct", producto.get("IdentifyingNumber")))
    valores.append(("SystemEnclosure", enclosure.get("SerialNumber")))
    valores.append(("BaseBoard", baseboard.get("SerialNumber")))

    return valores


def obtener_serial() -> str:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$bios = Get-CimInstance Win32_BIOS |
    Select-Object SerialNumber

$product = Get-CimInstance Win32_ComputerSystemProduct |
    Select-Object IdentifyingNumber, UUID, Name, Vendor

$enclosure = Get-CimInstance Win32_SystemEnclosure |
    Select-Object SerialNumber, SMBIOSAssetTag, ChassisTypes

$baseboard = Get-CimInstance Win32_BaseBoard |
    Select-Object SerialNumber, Product, Manufacturer

[PSCustomObject]@{
    Bios = $bios
    Product = $product
    Enclosure = $enclosure
    BaseBoard = $baseboard
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
            timeout=8,
        )

        if proc.returncode != 0 or not proc.stdout.strip():
            return "NO DETECTADO"

        data = json.loads(proc.stdout.strip())

        for _, valor in _extraer_valores(data):
            serial = _normalizar_serial(valor)

            if serial:
                return serial

        return "NO DETECTADO"

    except Exception:
        return "NO DETECTADO"