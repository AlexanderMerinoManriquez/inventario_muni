import subprocess


def obtener_serial():
    try:
        output = subprocess.check_output(
            "wmic bios get serialnumber",
            shell=True
        ).decode()

        return output.split("\n")[1].strip()

    except Exception:
        return "SERIAL_DESCONOCIDO"