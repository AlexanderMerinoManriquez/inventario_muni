import re
import os

def obtener_anydesk():
    rutas_posibles = [
        r"C:\ProgramData\AnyDesk\service.conf",
        r"C:\Program Files (x86)\AnyDesk\service.conf"
    ]

    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

               
                patrones = [
                    r"ad\.anynet\.id=(\d+)",
                    r"ad\.telemetry\.last_cid=(\d+)"
                ]

                for patron in patrones:
                    match = re.search(patron, contenido)
                    if match:
                        return match.group(1)

            except Exception:
                pass

    return "SIN_DEFINIR"