import json
import re
import subprocess

from utils.serial_utils import (
    normalizar_serial,
    extraer_serial_desde_ruta,
)


IMPRESORA_SERIAL_MIN_LEN = 5


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


TOKENS_IGNORADOS = {
    "printer",
    "impresora",
    "series",
    "serie",
    "driver",
    "pcl",
    "v4",
    "usb",
    "pro",
    "laserjet",
    "deskjet",
    "officejet",
}


SERIALES_IMPRESORA_INVALIDOS_EXTRA = {
    "PRINTQUEUE",
    "PRINTQUEUES",
    "PRINT QUEUE",
    "PRINT QUEUES",
    "LOCALPRINTQUEUE",
    "LOCAL PRINT QUEUE",
    "PRINTERQUEUE",
    "PRINTERQUEUES",
    "PRINTER QUEUE",
    "PRINTER QUEUES",
}


def _normalizar_texto(valor: str) -> str:
    return str(valor or "").strip()


def _normalizar_clave(valor: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(valor or "").lower())


def _compactar_serial(valor: str) -> str:
    return re.sub(r"[\s\-_\.]+", "", str(valor or "").upper())


def _normalizar_serial(valor: str) -> str:
    serial = str(valor or "").strip().upper().strip("{}")
    serial_compacto = _compactar_serial(serial)

    if serial in SERIALES_IMPRESORA_INVALIDOS_EXTRA:
        return ""

    if serial_compacto in {
        _compactar_serial(v)
        for v in SERIALES_IMPRESORA_INVALIDOS_EXTRA
    }:
        return ""

    return normalizar_serial(
        serial,
        min_len=IMPRESORA_SERIAL_MIN_LEN,
    ) or ""


def _extraer_serial_desde_ruta(valor: str) -> str:
    return extraer_serial_desde_ruta(
        valor,
        min_len=IMPRESORA_SERIAL_MIN_LEN,
    ) or ""


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


def _seriales_desde_lista(valores) -> list[str]:
    if not valores:
        return []

    if isinstance(valores, str):
        valores = [valores]

    seriales = []

    for valor in valores:
        serial = _extraer_serial_desde_ruta(valor)

        if serial and serial not in seriales:
            seriales.append(serial)

    return seriales


def _crear_regex_busqueda(nombre: str, driver: str) -> str:
    tokens = []

    for token in re.split(r"[^A-Za-z0-9]+", f"{nombre} {driver}"):
        t = token.strip()
        tl = t.lower()

        if len(t) >= 3 and tl not in TOKENS_IGNORADOS:
            tokens.append(re.escape(t))

    if tokens:
        return "|".join(dict.fromkeys(tokens))

    return (
        "hp|epson|canon|brother|xerox|ricoh|kyocera|samsung|"
        "laserjet|deskjet|officejet"
    )


def _pnp_puede_tener_serial_real(disp: dict) -> bool:
    pnp_class = _normalizar_texto(disp.get("PNPClass")).lower()
    service = _normalizar_texto(disp.get("Service")).lower()
    name = _normalizar_texto(disp.get("Name")).lower()
    device_id = _normalizar_texto(disp.get("DeviceID")).lower()
    pnp_device_id = _normalizar_texto(disp.get("PNPDeviceID")).lower()

    texto = f"{name} {device_id} {pnp_device_id}"

    if pnp_class == "printqueue":
        return False

    if "printqueue" in texto or "print queues" in texto:
        return False

    if "localprintqueue" in texto:
        return False

    if "printenum" in texto and service not in ("usbprint", "winusb"):
        return False

    if service in ("usbprint", "winusb"):
        return True

    return pnp_class in ("printer", "usbdevice", "usb")


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
        if not _pnp_puede_tener_serial_real(disp):
            continue

        nombre_pnp = _normalizar_texto(disp.get("Name"))
        device_id = _normalizar_texto(disp.get("DeviceID"))
        pnp_device_id = _normalizar_texto(disp.get("PNPDeviceID"))
        parent_device_id = _normalizar_texto(disp.get("ParentDeviceID"))
        bus_parent = _normalizar_texto(disp.get("BusParent"))
        seriales_usb = disp.get("SerialesUSB") or []

        nombre_pnp_key = _normalizar_clave(nombre_pnp)

        coincide = (
            nombre_key and nombre_key in nombre_pnp_key
        ) or (
            driver_key and driver_key in nombre_pnp_key
        ) or (
            nombre_pnp_key and nombre_pnp_key in nombre_key
        )

        if not coincide:
            continue

        for serial in _seriales_desde_lista(seriales_usb):
            if serial:
                return serial

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


def _obtener_pnp_rapido() -> tuple[list[dict], list[dict]]:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$excluir = 'microsoft print to pdf|microsoft xps document writer|onenote|fax|pdf|xps|snagit|cutepdf|send to onenote'

$printers = @(Get-CimInstance Win32_Printer |
    Select-Object Name, DriverName, PortName, WorkOffline, Default, PrinterStatus |
    Where-Object {
        $_.Name -and
        $_.WorkOffline -ne $true -and
        $_.Name.ToLower() -notmatch $excluir
    })

if ($printers.Count -eq 0) {
    [PSCustomObject]@{
        Printers = @()
        PnP = @()
    } | ConvertTo-Json -Depth 7 -Compress
    exit
}

$tokens = New-Object System.Collections.Generic.List[string]

foreach ($p in $printers) {
    $texto = "$($p.Name) $($p.DriverName)"

    foreach ($t in ($texto -split '[^A-Za-z0-9]+')) {
        $tl = $t.ToLower()

        if (
            $t.Length -ge 3 -and
            $tl -notin @(
                'printer',
                'impresora',
                'series',
                'serie',
                'driver',
                'pcl',
                'v4',
                'usb',
                'pro',
                'laserjet',
                'deskjet',
                'officejet'
            )
        ) {
            $tokens.Add([regex]::Escape($t))
        }
    }
}

if ($tokens.Count -eq 0) {
    $regex = 'hp|epson|canon|brother|xerox|ricoh|kyocera|samsung|laserjet|deskjet|officejet'
} else {
    $regex = ($tokens | Select-Object -Unique) -join '|'
}

$pnpBase = @(Get-CimInstance Win32_PnPEntity |
    Where-Object {
        ($_.Name -match $regex) -or
        ($_.DeviceID -match $regex) -or
        ($_.PNPDeviceID -match $regex) -or
        ($_.PNPClass -in @('Printer', 'USBDevice', 'USB') -and $_.Name -match $regex) -or
        ($_.Service -in @('usbprint', 'WINUSB') -and $_.Name -match $regex)
    })

$pnp = foreach ($d in $pnpBase) {
    $serialesUsb = New-Object System.Collections.Generic.List[string]

    $rutas = @(
        [string]$d.DeviceID,
        [string]$d.PNPDeviceID
    )

    foreach ($ruta in $rutas) {
        if ($ruta -match 'USB\\(VID_[0-9A-Fa-f]{4}&PID_[0-9A-Fa-f]{4})(?:&MI_[0-9A-Fa-f]{2})?\\') {
            $base = $Matches[1].ToUpper()
            $regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\USB\$base"

            if (Test-Path $regPath) {
                try {
                    Get-ChildItem $regPath -ErrorAction SilentlyContinue | ForEach-Object {
                        $leaf = Split-Path $_.Name -Leaf

                        if (
                            $leaf -and
                            $leaf -notmatch '&' -and
                            $leaf -notmatch '^[0-9A-Fa-f-]{36}$' -and
                            $leaf.ToUpper() -notin @(
                                'USB001',
                                'USB002',
                                'USB003',
                                'USB004',
                                'USB005',
                                'LPT1',
                                'LPT2',
                                'PRINTQUEUE',
                                'PRINTQUEUES',
                                'LOCALPRINTQUEUE'
                            )
                        ) {
                            $serialesUsb.Add("USB\$base\$leaf")
                        }
                    }
                } catch {}
            }
        }
    }

    [PSCustomObject]@{
        Name = $d.Name
        DeviceID = $d.DeviceID
        PNPDeviceID = $d.PNPDeviceID
        SerialesUSB = @($serialesUsb)
        ParentDeviceID = ""
        BusParent = ""
        Manufacturer = $d.Manufacturer
        Service = $d.Service
        PNPClass = $d.PNPClass
    }
}

[PSCustomObject]@{
    Printers = @($printers)
    PnP = @($pnp)
} | ConvertTo-Json -Depth 7 -Compress
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
            return [], []

        data = json.loads(proc.stdout.strip())

        impresoras_data = data.get("Printers") or []
        pnp_data = data.get("PnP") or []

        if isinstance(impresoras_data, dict):
            impresoras_data = [impresoras_data]

        if isinstance(pnp_data, dict):
            pnp_data = [pnp_data]

        return impresoras_data, pnp_data

    except Exception:
        return [], []


def _obtener_pnp_respaldo(nombre: str, driver: str) -> list[dict]:
    regex = _crear_regex_busqueda(nombre, driver)
    regex_ps = json.dumps(regex)

    script = rf"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$regex = {regex_ps}

$pnpBase = @(Get-CimInstance Win32_PnPEntity |
    Where-Object {{
        ($_.Name -match $regex) -or
        ($_.DeviceID -match $regex) -or
        ($_.PNPDeviceID -match $regex) -or
        ($_.PNPClass -in @('Printer', 'USBDevice', 'USB') -and $_.Name -match $regex) -or
        ($_.Service -in @('usbprint', 'WINUSB') -and $_.Name -match $regex)
    }})

$pnp = foreach ($d in $pnpBase) {{
    $parent = ""
    $busParent = ""

    try {{
        $propParent = Get-PnpDeviceProperty -InstanceId $d.PNPDeviceID -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue
        if ($propParent -and $propParent.Data) {{
            $parent = [string]$propParent.Data
        }}
    }} catch {{}}

    try {{
        $propBus = Get-PnpDeviceProperty -InstanceId $d.PNPDeviceID -KeyName '{{83DA6326-97A6-4088-9453-A1923F573B29}} 10' -ErrorAction SilentlyContinue
        if ($propBus -and $propBus.Data) {{
            $busParent = [string]$propBus.Data
        }}
    }} catch {{}}

    [PSCustomObject]@{{
        Name = $d.Name
        DeviceID = $d.DeviceID
        PNPDeviceID = $d.PNPDeviceID
        SerialesUSB = @()
        ParentDeviceID = $parent
        BusParent = $busParent
        Manufacturer = $d.Manufacturer
        Service = $d.Service
        PNPClass = $d.PNPClass
    }}
}}

@($pnp) | ConvertTo-Json -Depth 6 -Compress
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
            return []

        data = json.loads(proc.stdout.strip())

        if isinstance(data, dict):
            data = [data]

        return data

    except Exception:
        return []


def obtener_impresoras_activas() -> list[dict]:
    impresoras_data, pnp_data = _obtener_pnp_rapido()

    if not impresoras_data:
        return []

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

        if not serial:
            pnp_respaldo = _obtener_pnp_respaldo(nombre, driver)
            serial = _buscar_serial_impresora(nombre, driver, pnp_respaldo)

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