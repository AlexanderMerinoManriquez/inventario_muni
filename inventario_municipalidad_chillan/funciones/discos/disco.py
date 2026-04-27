import os
import psutil

def obtener_disco_principal():
    try:
        disco = round(psutil.disk_usage('C:/').total / (1024**3), 2)
    except:
        disco = round(psutil.disk_usage('/').total / (1024**3), 2)

    return f"{disco} GB"