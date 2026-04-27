import os
import sys
import shutil

def obtener_ruta_smart():

  
    ruta_exe = os.path.join(os.path.dirname(sys.executable), "smartctl.exe")
    if os.path.exists(ruta_exe):
        return ruta_exe

    ruta_local = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "herramientas", "smartctl.exe")
    )
    if os.path.exists(ruta_local):
        return ruta_local

  
    ruta_path = shutil.which("smartctl")
    if ruta_path:
        return ruta_path

    print(" smartctl no encontrado en ninguna ruta")
    return None