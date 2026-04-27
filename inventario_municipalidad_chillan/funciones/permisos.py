import ctypes
import sys
import time

def admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

if not admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
    except Exception:
        print("Hubo un error en los permisos de administrador de SMART")
        print("El programa se cerrará en 5 segundos...")
        time.sleep(5)
    
    sys.exit()
print("Smart ejecutándose con privilegios de administrador")