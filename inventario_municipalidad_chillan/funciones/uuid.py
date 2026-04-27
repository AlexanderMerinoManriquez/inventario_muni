import subprocess


def obtener_uuid():
    try:
        output = subprocess.check_output(
            "wmic csproduct get uuid",
            shell=True
        ).decode()

        return output.split("\n")[1].strip()

    except Exception:
        return "UUID_DESCONOCIDO"