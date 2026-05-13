import ctypes
import re
import socket
import subprocess
import unicodedata


MAX_NOMBRE_WINDOWS = 15


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


def _limpiar_segmento(texto: str, fallback: str, max_len: int) -> str:
    texto = _sin_tildes(texto)
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    return (texto[:max_len] or fallback)[:max_len]


def generar_nombre_equipo(departamento: str, funcionario: str) -> str:
    dep = _sin_tildes(departamento)

    if "-" in dep:
        dep_principal, subdepartamento = dep.split("-", 1)
    else:
        dep_principal, subdepartamento = dep, dep

    dep_code = _limpiar_segmento(dep_principal, "MUN", 3)
    sub_code = _codigo_subdepartamento(subdepartamento)

    funcionario = _sin_tildes(funcionario)
    partes = re.findall(r"[A-Z]+", funcionario)

    if len(partes) >= 2:
        apellido = partes[1]
    elif len(partes) == 1:
        apellido = partes[0]
    else:
        apellido = "USER"

    apellido = _limpiar_segmento(apellido, "USER", 9)

    nombre = f"{dep_code}-{sub_code}-{apellido}"
    return normalizar_nombre_windows(nombre)


def normalizar_nombre_windows(nombre: str) -> str:
    nombre = _sin_tildes(nombre)
    nombre = re.sub(r"[^A-Z0-9-]", "-", nombre)
    nombre = re.sub(r"-+", "-", nombre).strip("-")
    nombre = nombre[:MAX_NOMBRE_WINDOWS].strip("-")

    if not nombre:
        return "PC-MUNI"

    if nombre.isdigit():
        return f"PC-{nombre}"[:MAX_NOMBRE_WINDOWS].strip("-")

    return nombre


def validar_nombre_windows(nombre: str) -> tuple[bool, str]:
    if not nombre:
        return False, "El nombre del equipo está vacío."

    if len(nombre) > MAX_NOMBRE_WINDOWS:
        return False, "El nombre del equipo no puede superar 15 caracteres."

    if nombre.startswith("-") or nombre.endswith("-"):
        return False, "El nombre del equipo no puede comenzar ni terminar con guion."

    if not re.fullmatch(r"[A-Z0-9-]+", nombre):
        return False, "El nombre solo puede contener letras, números y guiones."

    if nombre.isdigit():
        return False, "El nombre del equipo no puede ser solo numérico."

    return True, ""


def es_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def renombrar_equipo(nuevo_nombre: str) -> tuple[bool, str]:
    nuevo_nombre = normalizar_nombre_windows(nuevo_nombre)
    es_valido, error = validar_nombre_windows(nuevo_nombre)

    if not es_valido:
        return False, error

    nombre_actual = socket.gethostname().upper()

    if nombre_actual == nuevo_nombre.upper():
        return True, "El equipo ya tiene ese nombre. No se realizaron cambios."

    if not es_admin():
        return False, "Debes ejecutar el programa como administrador para renombrar el equipo."

    comando = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"Rename-Computer -NewName '{nuevo_nombre}' -Force"
    ]

    try:
        proc = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    except subprocess.TimeoutExpired:
        return False, "La operación tardó demasiado y fue cancelada."

    except FileNotFoundError:
        return False, "No se encontró PowerShell en este equipo."

    except Exception as e:
        return False, f"Error inesperado al renombrar el equipo: {e}"

    salida = "\n".join(
        parte.strip()
        for parte in (proc.stdout, proc.stderr)
        if parte and parte.strip()
    )

    if proc.returncode == 0:
        return True, (
            f"Equipo renombrado a {nuevo_nombre}.\n\n"
            "Debes reiniciar Windows para aplicar completamente el cambio."
        )

    if salida:
        return False, salida

    return False, "Windows no pudo renombrar el equipo. Verifica permisos o políticas de dominio."