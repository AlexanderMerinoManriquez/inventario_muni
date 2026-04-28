import re
import subprocess
import unicodedata
import socket


def _sin_tildes(txt: str) -> str:
    txt = str(txt or "").upper().strip()
    return unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode()


def _codigo_subdepartamento(texto: str) -> str:
    palabras = re.findall(r"[A-Z0-9]+", texto)

    if not palabras:
        return "GEN"

    if len(palabras) == 1:
        return palabras[0][:3]

    return "".join(p[0] for p in palabras[:3])[:3]


def generar_nombre_equipo(departamento: str, funcionario: str) -> str:
    dep = _sin_tildes(departamento)

    if "-" in dep:
        dep_principal, subdepartamento = dep.split("-", 1)
    else:
        dep_principal, subdepartamento = dep, dep

    dep_code = re.sub(r"[^A-Z0-9]", "", dep_principal)[:3] or "MUN"
    sub_code = _codigo_subdepartamento(subdepartamento)

    funcionario = _sin_tildes(funcionario)
    partes = re.findall(r"[A-Z]+", funcionario)

    if len(partes) >= 2:
        apellido = partes[1]
    elif len(partes) == 1:
        apellido = partes[0]
    else:
        apellido = "USER"

    nombre = f"{dep_code}-{sub_code}-{apellido}"

    return nombre[:15] or "PC-MUNI"


def renombrar_equipo(nuevo_nombre: str) -> tuple[bool, str]:
    if socket.gethostname().upper() == nuevo_nombre.upper():
        return True, "El equipo ya tiene ese nombre. No se realizaron cambios."
    try:
        cmd = (
            f'wmic computersystem where name="%COMPUTERNAME%" '
            f'call rename name="{nuevo_nombre}"'
        )
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if proc.returncode == 0:
            return True, "Renombrado correctamente. Debes reiniciar el equipo."

        return False, (proc.stdout + proc.stderr).strip()

    except Exception as e:
        return False, str(e)