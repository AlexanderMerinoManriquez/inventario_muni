import json
import re
import subprocess

from funciones.tipo_equipo import detectar_tipo_equipo


VALORES_INVALIDOS = {
    "",
    "NONE",
    "UNKNOWN",
    "DESCONOCIDO",
    "NOT AVAILABLE",
    "NOT APPLICABLE",
    "SYSTEM PRODUCT NAME",
    "SYSTEM MANUFACTURER",
    "BASE BOARD",
    "BASEBOARD",
    "TO BE FILLED BY O.E.M.",
    "TO BE FILLED BY OEM",
    "TOBEFILLEDBYO.E.M.",
    "TOBEFILLEDBYOEM",
    "DEFAULT STRING",
    "DEFAULTSTRING",
    "SYSTEM VERSION",
    "VERSION",
    "OEM",
    "O.E.M.",
}


TIPOS_NOTEBOOK = (
    "notebook",
    "laptop",
    "portatil",
    "portátil",
    "portable",
    "mobile",
    "latitude",
    "thinkpad",
    "ideapad",
    "elitebook",
    "probook",
    "vivobook",
    "zenbook",
    "aspire",
    "swift",
)

TIPOS_ALL_IN_ONE = (
    "all in one",
    "all-in-one",
    "allinone",
    "aio",
    "todo en uno",
    "proone",
    "ideacentre aio",
    "ideacentre all in one",
)

TIPOS_TORRE = (
    "torre",
    "desktop",
    "escritorio",
    "ordenador",
    "pc de escritorio",
    "minitower",
    "tower",
    "workstation",
)


def _limpiar(valor) -> str:
    return str(valor or "").strip()


def _compactar(valor) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(valor or "").lower())


def _es_valor_util(valor) -> bool:
    texto = _limpiar(valor)
    texto_upper = texto.upper()
    texto_compacto = _compactar(texto).upper()

    if not texto:
        return False

    if texto_upper in VALORES_INVALIDOS:
        return False

    if texto_compacto in {
        "TOBEFILLEDBYOEM",
        "DEFAULTSTRING",
        "SYSTEMPRODUCTNAME",
        "SYSTEMMANUFACTURER",
        "SYSTEMVERSION",
        "NOTAPPLICABLE",
    }:
        return False

    if re.fullmatch(r"(v|ver|version|rev)?\.?\s*\d+(\.\d+)?", texto.lower()):
        return False

    return True


def _normalizar_marca(valor) -> str:
    texto = _limpiar(valor)

    if not _es_valor_util(texto):
        return ""

    base = texto.lower()

    marcas = {
        "hewlett-packard": "HP",
        "hewlett packard": "HP",
        "hp": "HP",
        "dell inc.": "Dell",
        "dell": "Dell",
        "lenovo": "Lenovo",
        "acer": "Acer",
        "asus": "ASUS",
        "asustek": "ASUS",
        "samsung": "Samsung",
        "microsoft": "Microsoft",
        "toshiba": "Toshiba",
        "dynabook": "Dynabook",
        "msi": "MSI",
        "micro-star": "MSI",
        "gigabyte": "Gigabyte",
        "apple": "Apple",
        "lg": "LG",
        "sony": "Sony",
        "huawei": "Huawei",
        "positivo": "Positivo",
        "compaq": "Compaq",
    }

    for clave, marca in marcas.items():
        if clave in base:
            return marca

    return texto


def _normalizar_tipo(valor) -> str | None:
    texto = _limpiar(valor).lower()
    compacto = _compactar(valor)

    if not texto:
        return None

    if any(p in texto for p in TIPOS_ALL_IN_ONE) or any(
        _compactar(p) in compacto for p in TIPOS_ALL_IN_ONE
    ):
        return "All in One"

    if any(p in texto for p in TIPOS_NOTEBOOK) or any(
        _compactar(p) in compacto for p in TIPOS_NOTEBOOK
    ):
        return "Notebook"

    if any(p in texto for p in TIPOS_TORRE) or any(
        _compactar(p) in compacto for p in TIPOS_TORRE
    ):
        return "Torre"

    return None


def _tipo_desde_chassis(chassis_types) -> str | None:
    try:
        tipos = chassis_types or []

        if isinstance(tipos, int):
            tipos = [tipos]

        tipos = [int(x) for x in tipos if str(x).strip().isdigit()]

    except Exception:
        tipos = []

    if 13 in tipos:
        return "All in One"

    if any(x in tipos for x in (8, 9, 10, 14, 30, 31, 32)):
        return "Notebook"

    if any(x in tipos for x in (3, 4, 5, 6, 7, 15, 16)):
        return "Torre"

    return None


def _elegir_modelo(data: dict, tipo: str) -> str:

    candidatos = [
        data.get("ProductVersion"),
        data.get("Model"),
        data.get("ProductName"),
    ]

    for candidato in candidatos:
        texto = _limpiar(candidato)

        if _es_valor_util(texto):
            return texto

    if tipo == "All in One":
        return "All in One"

    if tipo == "Notebook":
        return "Notebook"

    return "Equipo de torre"


def _obtener_info_equipo() -> dict:
    script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$cs = Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, PCSystemType
$csp = Get-CimInstance Win32_ComputerSystemProduct | Select-Object Vendor, Name, Version, IdentifyingNumber
$enclosure = Get-CimInstance Win32_SystemEnclosure | Select-Object ChassisTypes, SerialNumber

[PSCustomObject]@{
    Manufacturer = $cs.Manufacturer
    Model = $cs.Model
    PCSystemType = $cs.PCSystemType
    Vendor = $csp.Vendor
    ProductName = $csp.Name
    ProductVersion = $csp.Version
    IdentifyingNumber = $csp.IdentifyingNumber
    ChassisTypes = @($enclosure.ChassisTypes)
    EnclosureSerial = $enclosure.SerialNumber
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
            return {
                "marca": "Equipo",
                "modelo": "Equipo de torre",
                "tipo": "Torre",
            }

        data = json.loads(proc.stdout.strip())

    except Exception:
        return {
            "marca": "Equipo",
            "modelo": "Equipo de torre",
            "tipo": "Torre",
        }

    texto_equipo = " ".join(
        _limpiar(data.get(campo))
        for campo in (
            "Manufacturer",
            "Vendor",
            "Model",
            "ProductName",
            "ProductVersion",
        )
        if data.get(campo)
    )

    tipo = _tipo_desde_chassis(data.get("ChassisTypes"))
    tipo = tipo or _normalizar_tipo(texto_equipo)

    if not tipo:
        try:
            tipo_detectado = detectar_tipo_equipo()
            tipo = _normalizar_tipo(tipo_detectado)
        except Exception:
            tipo = None

    if not tipo:
        try:
            pc_system_type = int(data.get("PCSystemType") or 0)

            if pc_system_type == 2:
                tipo = "Notebook"
            elif pc_system_type in (1, 3):
                tipo = "Torre"

        except Exception:
            tipo = None

    tipo = tipo or "Torre"

    marca = (
        _normalizar_marca(data.get("Manufacturer"))
        or _normalizar_marca(data.get("Vendor"))
        or "Equipo"
    )

    modelo = _elegir_modelo(data, tipo)

    return {
        "marca": marca,
        "modelo": modelo,
        "tipo": tipo,
    }


_CACHE_INFO = None


def obtener_info_equipo() -> dict:
    global _CACHE_INFO

    if _CACHE_INFO is None:
        _CACHE_INFO = _obtener_info_equipo()

    return dict(_CACHE_INFO)


def obtener_marca_equipo() -> str:
    return obtener_info_equipo().get("marca", "Equipo")


def obtener_modelo_equipo() -> str:
    return obtener_info_equipo().get("modelo", "Equipo de torre")


def obtener_tipo_equipo_auto() -> str:
    return obtener_info_equipo().get("tipo", "Torre")