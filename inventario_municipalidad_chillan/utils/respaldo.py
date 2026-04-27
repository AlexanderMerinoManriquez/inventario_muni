import json
import os

from datetime import datetime
from config import RESPALDOS_DIR

def guardar_respaldo(data: dict, estado: str, respuesta: str = "") -> str:
    try:
        os.makedirs(RESPALDOS_DIR, exist_ok=True)
        ts     = datetime.now()
        nombre = str(data.get("nombre_pc", "sin_nombre")).replace(" ", "_")
        ruta   = os.path.join(RESPALDOS_DIR, f"ERROR_{ts:%Y%m%d_%H%M%S}_{nombre}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({
                "fecha":              ts.strftime("%Y-%m-%d %H:%M:%S"),
                "estado":             estado,
                "respuesta_servidor": respuesta,
                "datos_equipo":       data,
            }, f, ensure_ascii=False, indent=4)
        return ruta
    except Exception as e:
        return f"ERROR_AL_CREAR_RESPALDO: {e}"
