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


def _normalizar_texto(valor: str) -> str:
    return str(valor or "").strip()


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
    if any(x in base for x in ("mfp", "multifunction", "multifunc", "multifunción", "all-in-one")):
        return "multifuncional"
    return "impresora"


def _inferir_marca(nombre: str, driver: str) -> str:
    base = f"{nombre} {driver}".lower()
    marcas = {
        "hp": "HP",
        "hewlett packard": "HP",
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
        "laserjet", "laser", "mfp", "mfcl", "hl-", "ecosys",
        "workcentre", "imageclass", "bizhub", "ricoh", "xerox"
    )
    palabras_tinta = (
        "ink", "inkjet", "ecotank", "deskjet", "officejet",
        "stylus", "expression", "pixma", "tank"
    )
    
    if any(p in base for p in palabras_toner):
        return "tóner"

    if any(p in base for p in palabras_tinta):
        return "tinta"
    
    return ""


def obtener_impresoras_activas() -> list[dict]:
    script = r"""
$printers = Get-CimInstance Win32_Printer | Select-Object Name, DriverName, PortName, WorkOffline, Default, PrinterStatus
$printers | ConvertTo-Json -Compress
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )

        if proc.returncode != 0 or not proc.stdout.strip():
            return []

        data = json.loads(proc.stdout.strip())
        if isinstance(data, dict):
            data = [data]

        resultado = []
        for item in data:
            nombre = _normalizar_texto(item.get("Name"))
            driver = _normalizar_texto(item.get("DriverName"))
            puerto = _normalizar_texto(item.get("PortName"))
            offline = bool(item.get("WorkOffline"))

            if offline or not _es_impresora_real(nombre):
                continue

            marca = _inferir_marca(nombre, driver)
            modelo = _inferir_modelo(nombre, driver, marca).lower()

            resultado.append({
                "tipo": _inferir_tipo(nombre, driver),
                "marca": marca.lower(),
                "modelo": modelo,
                "ip": _extraer_ip(puerto),
                "toner_tinta": _sugerir_consumible(nombre, driver, modelo),
            })
        unicas = []
        vistos = set()
        for imp in resultado:
            clave = (imp["modelo"], imp["ip"], imp["tipo"])
            if clave in vistos:
                continue
            vistos.add(clave)
            unicas.append(imp)

        return unicas

    except Exception:
        return []