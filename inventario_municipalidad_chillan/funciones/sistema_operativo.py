import winreg
import platform

def obtener_sistema():
    key = None
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        product_name = winreg.QueryValueEx(key, "ProductName")[0]

        arquitectura = platform.machine()

        if arquitectura == "AMD64":
            arquitectura = "x64"

        sistema = f"{product_name} {arquitectura}"
        return sistema

    except Exception:
        return platform.system()

    finally:
        if key:
            winreg.CloseKey(key)
            