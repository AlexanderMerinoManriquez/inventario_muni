# -*- mode: python ; coding: utf-8 -*-
# inventario.spec — PyInstaller para Sistema de Inventario Municipalidad de Chillán
# Modo --onedir: carpeta portable + arranque más rápido que --onefile.

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules


# ── Recolectar paquetes que PyInstaller puede no detectar completo ───────────
wmi_datas,      wmi_binaries,      wmi_hidden      = collect_all("wmi")
psutil_datas,   psutil_binaries,   psutil_hidden   = collect_all("psutil")
requests_datas, requests_binaries, requests_hidden = collect_all("requests")

all_datas = wmi_datas + psutil_datas + requests_datas
all_binaries = wmi_binaries + psutil_binaries + requests_binaries
all_hidden = (
    wmi_hidden
    + psutil_hidden
    + requests_hidden
    + collect_submodules("wmi")
    + collect_submodules("psutil")
    + collect_submodules("requests")
    + collect_submodules("urllib3")
    + collect_submodules("charset_normalizer")
    + collect_submodules("certifi")
    + collect_submodules("funciones")
    + collect_submodules("utils")
    + collect_submodules("ui")
    + [
        "winreg",
        "win32api",
        "win32con",
        "win32security",
        "pywintypes",
        "pythoncom",
        "ctypes",
        "socket",
        "subprocess",
        "json",
        "re",
        "math",
        "logging",
        "logging.handlers",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
    ]
)


# ── Archivos externos incluidos dentro de la carpeta dist ────────────────────
# Nota: config.txt queda dentro de la distribución. Si algún día quieres cambiar
# la URL sin recompilar, conviene copiar/editar ese config.txt en la carpeta final.
added_datas = all_datas + [
    ("assets/Bannermuni.png", "assets"),
    ("assets/iconoMuni.png", "assets"),
    ("config.txt", "."),
]

# El icono del .exe debe ser .ico. El PNG se mantiene para Tkinter.
icon_path = "assets/iconoMuni.ico" if os.path.exists("assets/iconoMuni.ico") else None


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=all_binaries,
    datas=added_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "cv2",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "wx",
        "gi",
        "gtk",
        "test",
        "unittest",
        "xmlrpc",
        "ftplib",
        "imaplib",
        "poplib",
        "smtplib",
        "telnetlib",
        "http.server",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # Necesario para --onedir
    name="InventarioMunicipalidad",
    debug=False,
    strip=False,
    upx=False,                  # Más seguro para antivirus corporativo/municipal
    upx_exclude=[],
    console=False,              # Sin consola principal
    icon=icon_path,
    uac_admin=True,             # Solicita permisos de administrador al abrir
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,                  # Sin compresión UPX
    upx_exclude=[],
    name="InventarioMunicipalidad",
)
