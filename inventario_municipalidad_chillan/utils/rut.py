import re


def limpiar_rut(valor) -> str:
    rut = re.sub(r"[^0-9kK]", "", str(valor or "")).upper()
    return rut[:9]


def formatear_rut(valor) -> str | None:
    rut = limpiar_rut(valor)

    if not rut:
        return None

    if len(rut) < 7:
        return rut

    cuerpo = rut[:-1]
    dv = rut[-1]

    return f"{cuerpo}-{dv}"


def calcular_dv(cuerpo: str) -> str:
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1

        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    resultado = 11 - resto

    if resultado == 11:
        return "0"

    if resultado == 10:
        return "K"

    return str(resultado)

def es_rut_sospechoso(valor) -> bool:
    rut = limpiar_rut(valor)

    if len(rut) < 8:
        return True

    cuerpo = rut[:-1]

    if len(set(cuerpo)) == 1:
        return True

    if cuerpo in ("1234567", "12345678"):
        return True

    if cuerpo in ("7654321", "87654321"):
        return True

    return False


def validar_rut(valor) -> bool:
    rut = limpiar_rut(valor)

    if not re.fullmatch(r"\d{7,8}[0-9K]", rut):
        return False

    if es_rut_sospechoso(rut):
        return False

    cuerpo = rut[:-1]
    dv = rut[-1]

    return calcular_dv(cuerpo) == dv