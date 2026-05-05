import os
import socket

from funciones.anydesk import obtener_anydesk
from funciones.cpu import obtener_cpu
from funciones.ip import obtener_ip
from funciones.ram import obtener_ram
from funciones.serial import obtener_serial
from funciones.sistema_operativo import obtener_sistema

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH   = os.path.join(BASE_DIR, "config.txt")
RESPALDOS_DIR = os.path.join(BASE_DIR, "RESPALDOS_FALLIDOS")
ICON_PATH     = os.path.join(BASE_DIR, "assets", "iconoMuni.png")
BANNER_PATH   = os.path.join(BASE_DIR, "assets", "Bannermuni.png")

# ── Campos automáticos ────────────────────────────────────────────────────────
CAMPOS_AUTO = [
    ("nombre_pc",         socket.gethostname,   "Nombre PC"),
    ("sistema_operativo", obtener_sistema,       "Sistema operativo"),
    ("anydesk",           obtener_anydesk,       "AnyDesk"),
    ("cpu",               obtener_cpu,           "Procesador"),
    ("ram",               obtener_ram,           "RAM"),
    ("ip",                obtener_ip,            "IP"),
    ("serial",            obtener_serial,        "N° Serie"),
]

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "inventario_municipalidad",
    "charset": "utf8mb4",
}

CAMPOS_MONITOR   = [("marca", "Marca:"), ("modelo", "Modelo:"), ("pulgadas", "Pulgadas:")]
CAMPOS_IMPRESORA = [("tipo", "Tipo:"), ("marca", "Marca:"), ("modelo", "Modelo:"),
                    ("ip", "IP:"), ("toner_tinta", "Tóner / Tinta:")]

OBLIGATORIOS = {
    "usuario":             "Funcionario responsable",
    "registrado_por":      "Registrado por",
    "departamento_manual": "Departamento / dirección",
}
# ── Paleta institucional ───────────────────────────────────────────────────────
C = {
    "rojo":              "#C8102E",
    "rojo_hover":        "#a00d23",
    "rojo_light":        "#fce8ec",
    "rojo_dark":         "#8b0a1f",
    "blanco":            "#ffffff",
    "gris_bg":           "#f0f2f7",
    "gris_borde":        "#dde3ec",
    "gris_sub":          "#6b7a99",
    "gris_placeholder":  "#a0aec0",
    "texto":             "#1a2035",
    "texto_claro":       "#4a5568",
    "verde":             "#16783a",
    "verde_light":       "#e8f5ee",
    "amarillo":          "#b45309",
    "amarillo_light":    "#fef3c7",
    "azul_acento":       "#2563eb",
    "sombra":            "#e2e8f0",
    "badge_bg":          "#eef2ff",
    "badge_fg":          "#3730a3",
    "label_claro":       "#6f8fb3",
    "gris_panel":        "#f9fafb",
    "dropdown_sel":      "#fff0f3",
    "dropdown_sel_fg":   "#C8102E",
    "dropdown_hover":    "#f5f7ff",
    "gris_readonly":     "#f8f9fb",
    "rojo_estado":       "#C8102E",
    }