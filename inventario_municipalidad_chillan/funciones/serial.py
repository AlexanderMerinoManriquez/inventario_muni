import json
import subprocess

from utils.serial_utils import normalizar_serial


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
            serial = normalizar_serial(valor, min_len=5)

            if serial:
                return serial

        return "NO DETECTADO"

    except Exception:
        return "NO DETECTADO"