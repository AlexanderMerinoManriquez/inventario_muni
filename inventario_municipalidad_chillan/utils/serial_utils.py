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
    "USB005",
    "LPT1",
    "LPT2",
    "PORT",

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
    "PRINTQUEUE",
    "PRINTQUEUES",
    "PRINTERQUEUE",
    "MS_BTH",
    "UID",
)


def _compactar(valor: str) -> str:
    return re.sub(r"[\s\-_\.]+", "", str(valor or "").upper())


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

    serial_compacto = _compactar(serial)

    if serial in SERIALES_INVALIDOS or serial_compacto in SERIALES_INVALIDOS:
        return None

    if len(serial_compacto) < min_len:
        return None

    if es_guid(serial):
        return None

    for patron in PATRONES_SERIAL_INVALIDO:
        patron_compacto = _compactar(patron)

        if patron in serial or patron_compacto in serial_compacto:
            return None

    if "\\" in serial or "/" in serial:
        return None

    if "&" in serial:
        return None

    if len(set(serial_compacto)) == 1:
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