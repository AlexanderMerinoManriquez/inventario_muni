import subprocess

def obtener_serial():
    try:
        output = subprocess.check_output(
            'powershell "(Get-CimInstance Win32_BIOS).SerialNumber"',
            shell=True
        ).decode().strip()

        return output
    except:
        return "SERIAL_DESCONOCIDO"