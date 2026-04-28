import wmi

from .clasificacion import clasificar_tipo_disco


def obtener_discos_smart():
    c = wmi.WMI()
    discos = []

    for disk in c.Win32_DiskDrive():
        if str(disk.InterfaceType or "").upper() == "USB":
            continue

        modelo = str(disk.Model or "").strip()
        interfaz = str(disk.InterfaceType or "").strip()
        media_type = str(getattr(disk, "MediaType", "") or "").strip()
        caption = str(getattr(disk, "Caption", "") or "").strip()

        try:
            tamano = round(int(disk.Size or 0) / (1024**3), 2)
        except Exception:
            tamano = 0

        texto_tipo = f"{interfaz} {media_type} {caption}"
        tipo_disco = clasificar_tipo_disco(modelo, texto_tipo)

        discos.append({
            "modelo": modelo,
            "capacidad": f"{tamano} GB",
            "tipo": tipo_disco,
        })

    return discos