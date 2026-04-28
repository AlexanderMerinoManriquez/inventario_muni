import logging
import os
from datetime import datetime

def setup_logger():
    os.makedirs("logs", exist_ok=True)

    archivo = f"logs/inventario_{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        filename=archivo,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8"
    )