import psutil

def obtener_ram():
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    return f"{ram} GB"