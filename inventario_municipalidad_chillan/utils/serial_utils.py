import re

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
    "SIN SERIE",
    "SIN_SERIE",
    "N/A",
    "NA",
    "NULL",
    "ERROR",
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
    "USB001",
    "USB002",
    "USB003",
    "USB004",
    "LPT1",
    "LPT2",
    "PORT",
}

PATRONES_SERIAL_INVALIDO = (
    "WSD",
    "SWD\\",
    "USBPRINT\\",
    "PRINTENUM\\",
    "ROOT\\",
    "UMB\\",
    "BTH\\",
    "BTHENUM\\",
    "DISPLAY\\",
    "MONITOR\\",
    "PCI\\",
    "ACPI\\",
    "LOCALPRINTQUEUE",
    "MS_BTH",
    "UID",
)

def es_guid(valor: str) -> bool:
    return bool(
        re.fullmatch(
            r"\{?[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}?",
            str(valor or "").strip().upper(),
        )
    )

def normalizar_serial(valor, min_len: int = 3) -> str | None:
    serial = str(valor or "").strip().upper().strip("{}")

    if not serial:
        return None

    serial_compacto = re.sub(r"[\s\-_\.]+", "", serial)

    if serial in SERIALES_INVALIDOS or serial_compacto in SERIALES_INVALIDOS:
        return None

    if len(serial_compacto) < min_len:
        return None

    if es_guid(serial):
        return None

    if any(patron in serial for patron in PATRONES_SERIAL_INVALIDO):
        return None

    if "\\" in serial or "/" in serial:
        return None

    if "&" in serial:
        return None

    if re.fullmatch(r"0+", serial_compacto):
        return None

    if re.fullmatch(r"F+", serial_compacto):
        return None

    if re.fullmatch(r"X+", serial_compacto):
        return None

    return serial

def extraer_serial_desde_ruta(valor, min_len: int = 3) -> str | None:
    texto = str(valor or "").strip()

    if not texto:
        return None

    if "\\" not in texto:
        return normalizar_serial(texto, min_len=min_len)

    candidato = texto.split("\\")[-1].strip().strip("{}")
    candidato = re.sub(r"[^A-Za-z0-9\-_.]", "", candidato)

    return normalizar_serial(candidato, min_len=min_len)