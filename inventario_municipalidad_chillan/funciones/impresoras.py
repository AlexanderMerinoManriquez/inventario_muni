import json
import re
import subprocess


IMPRESORAS_EXCLUIDAS = (
    "microsoft print to pdf",
    "microsoft xps document writer",
    "onenote",
    "fax",
    "pdf",
    "xps",
    "snagit",
    "cutepdf",
    "send to onenote",
)

SERIALES_INVALIDOS = {
    "",
    "0",
    "00",
    "000",
    "0000",
    "00000",
    "000000",
    "NONE",
    "UNKNOWN",
    "DESCONOCIDO",
    "NO DETECTADO",
    "SIN SERIAL",
    "SIN_SERIE",
    "N/A",
    "NA",
}


def _normalizar_texto(valor: str) -> str:
    return str(valor or "").strip()


def _normalizar_clave(valor: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(valor or "").lower())


def _normalizar_serial(valor: str) -> str:
    serial = str(valor or "").strip().upper()

    if serial in SERIALES_INVALIDOS:
        return ""

    if len(serial) < 5:
        return ""

    return serial


def _es_impresora_real(nombre: str) -> bool:
    nombre_l = _normalizar_texto(nombre).lower()

    if not nombre_l:
        return False

    return not any(x in nombre_l for x in IMPRESORAS_EXCLUIDAS)


def _inferir_tipo(nombre: str, driver: str) -> str:
    base = f"{nombre} {driver}".lower()

    if "plotter" in base:
        return "plotter"

    if "scanner" in base and "multif" not in base:
        return "scanner"

    if any(x in base for x in (
        "mfp",
        "multifunction",
        "multifunc",
        "multifunción",
        "all-in-one",
    )):
        return "multifuncional"

    return "impresora"


def _inferir_marca(nombre: str, driver: str) -> str:
    base = f"{nombre} {driver}".lower()

    marcas = {
        "hewlett packard": "HP",
        "hp": "HP",
        "epson": "Epson",
        "brother": "Brother",
        "canon": "Canon",
        "lexmark": "Lexmark",
        "xerox": "Xerox",
        "ricoh": "Ricoh",
        "kyocera": "Kyocera",
        "samsung": "Samsung",
        "oki": "OKI",
        "pantum": "Pantum",
        "sharp": "Sharp",
        "konica": "Konica Minolta",
        "minolta": "Konica Minolta",
    }

    for clave, marca in marcas.items():
        if clave in base:
            return marca

    return ""


def _inferir_modelo(nombre: str, driver: str, marca: str) -> str:
    candidato = _normalizar_texto(nombre) or _normalizar_texto(driver)

    if not candidato:
        return ""

    if marca and candidato.lower().startswith(marca.lower()):
        return candidato

    return candidato


def _extraer_ip(puerto: str) -> str:
    puerto = _normalizar_texto(puerto)
    match = re.search(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", puerto)
    return match.group(1) if match else ""


def _sugerir_consumible(nombre: str, driver: str, modelo: str = "") -> str:
    base = f"{nombre} {driver} {modelo}".lower()

    palabras_toner = (
        "laserjet",
        "laser",
        "mfp",
        "mfcl",
        "hl-",
        "ecosys",
        "workcentre",
        "imageclass",
        "bizhub",
        "ricoh",
        "xerox",
    )

    palabras_tinta = (
        "ink",
        "inkjet",
        "ecotank",
        "deskjet",
        "officejet",
        "stylus",
        "expression",
        "pixma",
        "tank",
    )

    if any(p in base for p in palabras_toner):
        return "tóner"

    if any(p in base for p in palabras_tinta):
        return "tinta"

    return ""


def _extraer_serial_desde_pnp(device_id: str) -> str:
    """
    Intenta extraer un serial desde DeviceID/PNPDeviceID.

    Se evita usar valores con '&' porque normalmente son rutas internas
    de Windows y pueden no corresponder al serial real del equipo.
    """
    texto = _normalizar_texto(device_id)

    if not texto or "\\" not in texto:
        return ""

    candidato = texto.split("\\")[-1].strip()

    if "&" in candidato:
        return ""

    candidato = re.sub(r"[^A-Za-z0-9\-_.]", "", candidato)
    return _normalizar_serial(candidato)


def _buscar_serial_impresora(
    nombre: str,
    driver: str,
    dispositivos_pnp: list[dict],
) -> str:
    nombre_key = _normalizar_clave(nombre)
    driver_key = _normalizar_clave(driver)

    if not nombre_key and not driver_key:
        return ""

    for disp in dispositivos_pnp:
        nombre_pnp = _normalizar_texto(disp.get("Name"))
        device_id = _normalizar_texto(
            disp.get("DeviceID")
            or disp.get("PNPDeviceID")
        )

        nombre_pnp_key = _normalizar_clave(nombre_pnp)

        if not nombre_pnp_key:
            continue

        coincide = (
            nombre_key and nombre_key in nombre_pnp_key
        ) or (
            driver_key and driver_key in nombre_pnp_key
        ) or (
            nombre_pnp_key and nombre_pnp_key in nombre_key
        )

        if not coincide:
            continue

        serial = _extraer_serial_desde_pnp(device_id)

        if serial:
            return serial

    return ""


def obtener_impresoras_activas() -> list[dict]:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$printers = Get-CimInstance Win32_Printer |
    Select-Object Name, DriverName, PortName, WorkOffline, Default, PrinterStatus

$pnp = Get-CimInstance Win32_PnPEntity |
    Where-Object {
        $_.PNPClass -in @('Printer', 'PrintQueue') -or
        $_.Service -eq 'usbprint' -or
        $_.Name -match 'printer|laserjet|deskjet|officejet|epson|canon|brother|xerox|ricoh|kyocera|samsung'
    } |
    Select-Object Name, DeviceID, PNPDeviceID, Manufacturer, Service, PNPClass

[PSCustomObject]@{
    Printers = @($printers)
    PnP = @($pnp)
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
            timeout=25,
        )

        if proc.returncode != 0 or not proc.stdout.strip():
            return []

        data = json.loads(proc.stdout.strip())

        impresoras_data = data.get("Printers") or []
        pnp_data = data.get("PnP") or []

        if isinstance(impresoras_data, dict):
            impresoras_data = [impresoras_data]

        if isinstance(pnp_data, dict):
            pnp_data = [pnp_data]

        resultado = []

        for item in impresoras_data:
            nombre = _normalizar_texto(item.get("Name"))
            driver = _normalizar_texto(item.get("DriverName"))
            puerto = _normalizar_texto(item.get("PortName"))
            offline = bool(item.get("WorkOffline"))

            if offline or not _es_impresora_real(nombre):
                continue

            marca = _inferir_marca(nombre, driver)
            modelo = _inferir_modelo(nombre, driver, marca).lower()
            serial = _buscar_serial_impresora(nombre, driver, pnp_data)

            resultado.append({
                "tipo": _inferir_tipo(nombre, driver),
                "marca": marca.lower(),
                "modelo": modelo,
                "ip": _extraer_ip(puerto),
                "toner_tinta": _sugerir_consumible(nombre, driver, modelo),
                "numero_de_serie": serial,
            })

        unicas = []
        vistos = set()

        for imp in resultado:
            clave = (
                imp.get("modelo", ""),
                imp.get("ip", ""),
                imp.get("tipo", ""),
                imp.get("numero_de_serie", ""),
            )

            if clave in vistos:
                continue

            vistos.add(clave)
            unicas.append(imp)

        return unicas

    except Exception:
        return []