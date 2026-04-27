# ── Formateo de capacidad ──────────────────────────────────────────────────────
def formatear_capacidad(valor: str) -> str:
    texto  = str(valor or "").strip().replace(",", ".")
    partes = texto.split()
    if not partes:
        return texto
    try:
        numero = float(partes[0])
        unidad = partes[1].upper() if len(partes) > 1 else "GB"
        return f"{round(numero)} {unidad}"
    except Exception:
        return texto
