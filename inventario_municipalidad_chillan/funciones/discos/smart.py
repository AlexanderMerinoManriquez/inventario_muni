import subprocess
import re

from funciones.discos.utils import obtener_ruta_smart


def detectar_discos():
    ruta = obtener_ruta_smart()

    if not ruta:
        print("smartctl no encontrado")
        return []

    dispositivos = []

    try:
        salida = subprocess.check_output(
            [ruta, "--scan"],
            text=True,
            timeout=5
        )
    except Exception as e:
        print("Error escaneando discos:", e)
        return []

    for linea in salida.splitlines():

        l = linea.lower().strip()

        if not l:
            continue

    
        if "usb" in l or "cdrom" in l or "loop" in l:
            continue

        match = re.search(r"(/dev/\S+)\s+-d\s+(\S+)", linea)

        if match:
            device = match.group(1)
            tipo = match.group(2)

            dispositivos.append((device, tipo))

    return dispositivos


def obtener_info_smart(device, tipo):
    ruta = obtener_ruta_smart()

    salud = "DESCONOCIDO"
    horas = None
    errores = 0
    temperatura = None

    try:
        salida = subprocess.check_output(
            [ruta, "-H", device, "-d", tipo],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL
        )

        if "PASSED" in salida.upper():
            salud = "OK"
        elif "FAILED" in salida.upper():
            salud = "FALLA"

    except Exception:
        return None  # si falla, ignoramos el disco

    try:
        salida = subprocess.check_output(
            [ruta, "-A", device, "-d", tipo],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL
        )

        for linea in salida.splitlines():

            l = linea.lower()

            if "power_on_hours" in l:
                nums = re.findall(r"\d+", linea)
                if nums:
                    horas = int(nums[-1])

            if "temperature" in l:
                nums = re.findall(r"\d+", linea)
                if nums:
                    temperatura = int(nums[-1])

            if "reallocated" in l or "pending" in l or "uncorrectable" in l:
                nums = re.findall(r"\d+", linea)
                if nums:
                    errores += int(nums[-1])

    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass

    return {
        "device": device,
        "tipo": tipo,
        "salud": salud,
        "horas": horas,
        "errores": errores,
        "temperatura": temperatura
    }


def obtener_discos_smart():
    dispositivos = detectar_discos()

    discos = []

    for device, tipo in dispositivos:
        info = obtener_info_smart(device, tipo)

        if info:
            discos.append(info)

    return discos