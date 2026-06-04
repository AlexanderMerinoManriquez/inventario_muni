import logging
import os

from datetime import datetime
from logging.handlers import RotatingFileHandler

from config import BASE_DIR


MAX_ARCHIVOS_LOG = 15
MAX_BYTES_POR_LOG = 2 * 1024 * 1024


def setup_logger() -> None:
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_log = os.path.join(logs_dir, f"inventario_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        archivo_log,
        maxBytes=MAX_BYTES_POR_LOG,
        backupCount=MAX_ARCHIVOS_LOG,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    try:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    except Exception:
        pass  

    logging.info("Logger inicializado. Archivo: %s", archivo_log)


def limpiar_logs_antiguos(max_archivos: int = MAX_ARCHIVOS_LOG) -> None:
    logs_dir = os.path.join(BASE_DIR, "logs")

    if not os.path.isdir(logs_dir):
        return

    try:
        archivos = sorted(
            [
                os.path.join(logs_dir, f)
                for f in os.listdir(logs_dir)
                if f.startswith("inventario_") and f.endswith(".log")
            ],
            key=os.path.getmtime,
        )

        for archivo_viejo in archivos[:-max_archivos]:
            try:
                os.remove(archivo_viejo)
                logging.debug("Log antiguo eliminado: %s", archivo_viejo)
            except Exception:
                pass

    except Exception:
        pass