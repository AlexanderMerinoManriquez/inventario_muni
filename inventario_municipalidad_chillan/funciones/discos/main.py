import wmi

from .smart import detectar_discos, obtener_info_smart
from .salud import calcular_salud
from .clasificacion import clasificar_tipo_disco


def obtener_discos_smart():

    c = wmi.WMI()

    dispositivos = detectar_discos()

    discos = []

    for i, disk in enumerate(c.Win32_DiskDrive()):

  
        if disk.InterfaceType == "USB":
            continue

        modelo = disk.Model
        tamano = round(int(disk.Size) / (1024**3), 2)

        espacio_libre = 0

        for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical in partition.associators("Win32_LogicalDiskToPartition"):
                espacio_libre += int(logical.FreeSpace)

        espacio_libre = round(espacio_libre / (1024**3), 2)

        # 🔹 Valores por defecto
        horas = 0
        salud = "DESCONOCIDO"
        errores = 0
        temperatura = None
        tipo = "desconocido"

        if i < len(dispositivos):

            device, tipo = dispositivos[i]

            info = obtener_info_smart(device, tipo)

            if info:
                horas = info["horas"] or 0
                salud = info["salud"]
                errores = info["errores"] or 0
                temperatura = info["temperatura"]

       
        porcentaje = calcular_salud(horas, errores, temperatura)
        tipo_disco = clasificar_tipo_disco(modelo, tipo)

        discos.append({
            "modelo": modelo,
            "capacidad": f"{tamano} GB",
            "espacio_libre_gb": espacio_libre,
            "tipo": tipo_disco,
            "salud": f"{porcentaje}%",
            "horas": horas,
            "errores": errores,
            "temperatura": temperatura if temperatura else "N/A"
        })

    return discos