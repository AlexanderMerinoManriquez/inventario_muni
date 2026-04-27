from tkinter import ttk
from config import C


def configurar_estilo() -> None:
    s = ttk.Style()

    try:
        s.theme_use("clam")
    except Exception:
        pass

    s.configure(
        ".",
        background=C["gris_bg"],
        foreground=C["texto"],
        font=("Segoe UI", 10),
    )

    s.configure("TFrame", background=C["gris_bg"])
    s.configure("TLabel", background=C["gris_bg"], foreground=C["texto"])

    s.configure(
        "Section.TLabelframe",
        background=C["gris_panel"],
        bordercolor=C["gris_borde"],
        relief="solid",
        borderwidth=1,
    )

    s.configure(
        "Section.TLabelframe.Label",
        background=C["gris_bg"],
        foreground=C["rojo"],
        font=("Segoe UI", 10, "bold"),
    )

    s.configure(
        "TEntry",
        fieldbackground=C["blanco"],
        bordercolor=C["gris_borde"],
        padding=6,
        relief="flat",
    )

    s.map(
        "TEntry",
        bordercolor=[("focus", C["rojo"]), ("!focus", C["gris_borde"])],
        fieldbackground=[("readonly", C["gris_readonly"])],
    )

    s.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(22, 9),
        background=C["rojo"],
        foreground=C["blanco"],
        borderwidth=0,
        relief="flat",
    )

    s.map(
        "Primary.TButton",
        background=[
            ("active", C["rojo_hover"]),
            ("pressed", C["rojo_dark"]),
            ("disabled", C["gris_borde"]),
        ],
        foreground=[
            ("active", C["blanco"]),
            ("disabled", C["gris_sub"]),
        ],
    )

    s.configure(
        "Danger.TButton",
        font=("Segoe UI", 10),
        padding=(22, 9),
        background=C["rojo_light"],
        foreground=C["rojo"],
        borderwidth=0,
        relief="flat",
    )

    s.map(
        "Danger.TButton",
        background=[("active", "#f9cdd4")],
        foreground=[("active", C["rojo_dark"])],
    )

    s.configure(
        "TButton",
        font=("Segoe UI", 9),
        padding=(10, 4),
        background="#eaeff6",
        foreground=C["texto"],
        bordercolor=C["gris_borde"],
        borderwidth=1,
        relief="flat",
    )

    s.map(
        "TButton",
        background=[("active", "#d8e2ef")],
    )

    s.configure(
        "Small.TButton",
        font=("Segoe UI", 8),
        padding=(7, 4),
        background="#eaeff6",
        foreground=C["texto"],
        bordercolor=C["gris_borde"],
        borderwidth=1,
        relief="flat",
    )

    s.map(
        "Small.TButton",
        background=[("active", "#d8e2ef")],
    )

    s.configure(
        "Edit.TButton",
        font=("Segoe UI", 8, "bold"),
        padding=(8, 4),
        background="#eaf2ff",
        foreground="#1d4ed8",
        bordercolor="#bcd4f6",
        borderwidth=1,
        relief="flat",
    )

    s.map(
        "Edit.TButton",
        background=[("active", "#dbeafe")],
        foreground=[("active", "#1e40af")],
    )

    s.configure(
        "Add.TButton",
        font=("Segoe UI", 8, "bold"),
        padding=(8, 4),
        background=C["verde_light"],
        foreground=C["verde"],
        bordercolor="#b7dfc5",
        borderwidth=1,
        relief="flat",
    )

    s.map(
        "Add.TButton",
        background=[("active", "#d8f3e1")],
        foreground=[("active", "#0f5c2b")],
    )

    s.configure(
        "Remove.TButton",
        font=("Segoe UI", 8),
        padding=(7, 3),
        background=C["rojo_light"],
        foreground=C["rojo"],
        bordercolor="#efb5c0",
        borderwidth=1,
        relief="flat",
    )

    s.map(
        "Remove.TButton",
        background=[("active", "#f9cdd4")],
        foreground=[("active", C["rojo_dark"])],
    )

    s.configure(
        "Vertical.TScrollbar",
        background=C["gris_bg"],
        troughcolor=C["sombra"],
        bordercolor=C["gris_bg"],
        arrowsize=12,
        relief="flat",
    )

    s.map(
        "Vertical.TScrollbar",
        background=[("active", C["gris_borde"])],
    )