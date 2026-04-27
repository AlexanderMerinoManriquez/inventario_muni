import subprocess

def obtener_uuid():
    try:
        output = subprocess.check_output(
            'powershell "(Get-CimInstance Win32_ComputerSystemProduct).UUID"',
            shell=True
        ).decode()

        return output.strip()

    except:
        return "UUID_DESCONOCIDO"