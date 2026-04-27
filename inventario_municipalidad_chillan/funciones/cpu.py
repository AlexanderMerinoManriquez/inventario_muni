import wmi
import subprocess
import platform

def limpiar_cpu(cpu):

    cpu = cpu.replace("(R)", "")
    cpu = cpu.replace("(TM)", "")
    cpu = cpu.replace("CPU", "")
    cpu = cpu.replace("with Radeon Graphics", "")

    cpu = " ".join(cpu.split())

    return cpu.strip()


def obtener_cpu():

    cpu = None

    try:
        c = wmi.WMI()
        cpu = c.Win32_Processor()[0].Name.strip()

        if "Family" not in cpu:
            return limpiar_cpu(cpu)

    except:
        pass

    try:
        output = subprocess.check_output(
            'powershell "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"',
            shell=True
        ).decode().strip()

        if output and "Family" not in output:
            return limpiar_cpu(output)

    except:
        pass

    try:
        output = subprocess.check_output(
            "wmic cpu get name",
            shell=True
        ).decode()

        cpu = output.split("\n")[1].strip()

        if cpu and "Family" not in cpu:
            return limpiar_cpu(cpu)

    except:
        pass

    try:
        cpu = platform.processor()

        if cpu:
            return limpiar_cpu(cpu)

    except:
        pass

    return "CPU_DESCONOCIDA"