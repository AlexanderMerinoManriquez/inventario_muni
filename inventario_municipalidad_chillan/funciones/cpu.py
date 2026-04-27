import winreg


def limpiar_cpu(cpu: str) -> str:
    cpu = str(cpu or "")
    cpu = cpu.replace("(R)", "")
    cpu = cpu.replace("(TM)", "")
    cpu = cpu.replace("CPU", "")
    cpu = cpu.replace("with Radeon Graphics", "")
    return " ".join(cpu.split()).strip()


def obtener_cpu() -> str:
    try:
        ruta = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ruta) as key:
            nombre, _ = winreg.QueryValueEx(key, "ProcessorNameString")

        cpu = limpiar_cpu(nombre)

        if cpu and "Family" not in cpu:
            return cpu

    except Exception:
        pass

    return "CPU_DESCONOCIDA"