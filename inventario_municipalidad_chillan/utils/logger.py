import logging
import os

from datetime import datetime
from config import BASE_DIR


def setup_logger() -> None:
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    archivo_log = os.path.join(
        logs_dir,
        f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logging.basicConfig(
        filename=archivo_log,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
        force=True,
    )