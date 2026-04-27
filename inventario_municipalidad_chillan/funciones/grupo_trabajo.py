import subprocess


def obtener_grupo_trabajo():
    try:
        output = subprocess.check_output(
            "wmic computersystem get workgroup",
            shell=True
        ).decode()

        valor = output.split("\n")[1].strip()
        return valor if valor else "SIN_DEFINIR"

    except Exception:
        return "SIN_DEFINIR"