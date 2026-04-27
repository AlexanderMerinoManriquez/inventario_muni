import wmi

from .clasificacion import clasificar_tipo_disco


def obtener_discos_smart():
    c = wmi.WMI()
    discos = []

    for disk in c.Win32_DiskDrive():
        if str(disk.InterfaceType).upper() == "USB":
            continue

        modelo = str(disk.Model or "").strip()
        tamano = round(int(disk.Size or 0) / (1024**3), 2)

        tipo_disco = clasificar_tipo_disco(modelo, "")

        discos.append({
            "modelo": modelo,
            "capacidad": f"{tamano} GB",
            "tipo": tipo_disco,
        })

    return discos