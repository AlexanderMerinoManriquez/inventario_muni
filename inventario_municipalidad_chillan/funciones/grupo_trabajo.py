import subprocess

def obtener_grupo_trabajo():
    try:
        resultado = subprocess.check_output(
            'powershell "(Get-WmiObject Win32_ComputerSystem).Workgroup"',
            shell=True
        ).decode(errors="ignore").strip()

        if resultado:
            return resultado

    except Exception as e:
        print("Error obteniendo grupo de trabajo:", e)

    return "SIN_DEFINIR"