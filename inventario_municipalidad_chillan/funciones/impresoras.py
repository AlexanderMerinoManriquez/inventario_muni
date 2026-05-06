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
    "USB001",
    "USB002",
    "USB003",
}


def _normalizar_texto(valor: str) -> str:
    return str(valor or "").strip()


def _normalizar_clave(valor: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(valor or "").lower())


def _es_guid(valor: str) -> bool:
    return bool(
        re.fullmatch(
            r"\{?[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}?",
            str(valor or "").strip().upper(),
        )
    )


def _normalizar_serial(valor: str) -> str:
    serial = str(valor or "").strip().upper().strip("{}")

    if serial in SERIALES_INVALIDOS:
        return ""

    if len(serial) < 5:
        return ""

    # Rechaza GUID/UUID de Windows, WSD o PnP.
    if _es_guid(serial):
        return ""

    patrones_invalidos = (
        "WSD",
        "SWD\\",
        "USBPRINT\\",
        "ROOT\\",
        "PRINTENUM\\",
        "UMB\\",
        "BTH\\",
        "BTHENUM\\",
        "MS_BTH",
    )

    if any(p in serial for p in patrones_invalidos):
        return ""

    # Si contiene separadores de ruta, no debe llegar completo como serial.
    if "\\" in serial or "/" in serial:
        return ""

    # Si contiene &, normalmente es parte de una ruta interna de Windows.
    if "&" in serial:
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


def _extraer_serial_desde_ruta(valor: str) -> str:
    """
    Extrae un posible serial desde rutas PnP/USB.

    Ejemplo válido:
    USB\\VID_03F0&PID_0274\\BRBSTB80DJ
    → BRBSTB80DJ

    Ejemplos inválidos:
    SWD\\PRINTENUM\\{C4583CAA-53E3-4B23-8319-DE7BA2CDF018}
    USBPRINT\\HPHP_LASERJET_PRO_4003\\8&315C8AC&0&USB001
    USB\\VID_03F0&PID_0274&MI_03\\7&38FDD011&1&C003
    """
    texto = _normalizar_texto(valor)

    if not texto or "\\" not in texto:
        return _normalizar_serial(texto)

    candidato = texto.split("\\")[-1].strip()
    candidato = candidato.strip("{}")
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
        device_id = _normalizar_texto(disp.get("DeviceID"))
        pnp_device_id = _normalizar_texto(disp.get("PNPDeviceID"))
        parent_device_id = _normalizar_texto(disp.get("ParentDeviceID"))
        bus_parent = _normalizar_texto(disp.get("BusParent"))

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

        # Prioridad 1: ParentDeviceID, porque ahí Windows suele exponer el serial USB real.
        for candidato in (
            parent_device_id,
            bus_parent,
            device_id,
            pnp_device_id,
        ):
            serial = _extraer_serial_desde_ruta(candidato)

            if serial:
                return serial

    return ""


def obtener_impresoras_activas() -> list[dict]:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$printers = Get-CimInstance Win32_Printer |
    Select-Object Name, DriverName, PortName, WorkOffline, Default, PrinterStatus

$pnpBase = Get-CimInstance Win32_PnPEntity |
    Where-Object {
        $_.PNPClass -in @('Printer', 'PrintQueue', 'USBDevice', 'USB') -or
        $_.Service -eq 'usbprint' -or
        $_.Service -eq 'WINUSB' -or
        $_.Name -match 'printer|laserjet|deskjet|officejet|epson|canon|brother|xerox|ricoh|kyocera|samsung|hp'
    }

$pnp = foreach ($d in $pnpBase) {
    $parent = ""
    $busParent = ""

    try {
        $propParent = Get-PnpDeviceProperty -InstanceId $d.PNPDeviceID -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue
        if ($propParent -and $propParent.Data) {
            $parent = [string]$propParent.Data
        }
    } catch {}

    try {
        $propBus = Get-PnpDeviceProperty -InstanceId $d.PNPDeviceID -KeyName '{83DA6326-97A6-4088-9453-A1923F573B29} 10' -ErrorAction SilentlyContinue
        if ($propBus -and $propBus.Data) {
            $busParent = [string]$propBus.Data
        }
    } catch {}

    [PSCustomObject]@{
        Name = $d.Name
        DeviceID = $d.DeviceID
        PNPDeviceID = $d.PNPDeviceID
        ParentDeviceID = $parent
        BusParent = $busParent
        Manufacturer = $d.Manufacturer
        Service = $d.Service
        PNPClass = $d.PNPClass
    }
}

[PSCustomObject]@{
    Printers = @($printers)
    PnP = @($pnp)
} | ConvertTo-Json -Depth 6 -Compress
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
            timeout=30,
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
            ip = _extraer_ip(puerto)
            serial = _buscar_serial_impresora(nombre, driver, pnp_data)

            resultado.append({
                "tipo": _inferir_tipo(nombre, driver),
                "marca": marca.lower(),
                "modelo": modelo,
                "ip": ip,
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