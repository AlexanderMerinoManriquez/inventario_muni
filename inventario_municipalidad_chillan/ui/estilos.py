from tkinter import ttk
from config import C

def configurar_estilo() -> None:
    s = ttk.Style()
    try:
        s.theme_use("clam")
    except Exception:
        pass
    s.configure(".", background=C["gris_bg"], foreground=C["texto"],
                font=("Segoe UI", 10))
    s.configure("TFrame",  background=C["gris_bg"])
    s.configure("TLabel",  background=C["gris_bg"], foreground=C["texto"])
    s.configure("Section.TLabelframe",
                background=C["gris_panel"], bordercolor=C["gris_borde"],
                relief="solid", borderwidth=1)
    s.configure("Section.TLabelframe.Label",
                background=C["gris_bg"], foreground=C["rojo"],
                font=("Segoe UI", 10, "bold"))
    s.configure("TEntry",
                fieldbackground=C["gris_panel"],
                bordercolor=C["gris_borde"], padding=6)
    s.configure("Primary.TButton",
                font=("Segoe UI", 10, "bold"), padding=(22, 9),
                background=C["rojo"], foreground="white", borderwidth=0)
    s.map("Primary.TButton",
          background=[("active", C["rojo_hover"]), ("pressed", C["rojo_dark"])],
          foreground=[("active", "white")])
    s.configure("TButton", font=("Segoe UI", 9), padding=(10, 4),
                background="#eaeff6", bordercolor=C["gris_borde"])
    s.map("TButton", background=[("active", "#d8e2ef")])
    s.configure("Small.TButton", font=("Segoe UI", 8), padding=(6, 3),
                background="#eaeff6", bordercolor=C["gris_borde"])
    s.map("Small.TButton", background=[("active", "#d8e2ef")])
    s.configure("Danger.TButton", font=("Segoe UI", 10), padding=(22, 9),
                background=C["rojo_light"], foreground=C["rojo"], borderwidth=0)
    s.map("Danger.TButton", background=[("active", "#f9cdd4")])
    s.configure("Edit.TButton", font=("Segoe UI", 8), padding=(5, 3),
                background=C["badge_bg"], foreground=C["badge_fg"], borderwidth=0)
    s.map("Edit.TButton",
          background=[("active", "#dde7ff")],
          foreground=[("active", C["azul_acento"])])
    s.configure("Vertical.TScrollbar",
                background=C["gris_bg"], troughcolor=C["sombra"],
                bordercolor=C["gris_bg"], arrowsize=12)