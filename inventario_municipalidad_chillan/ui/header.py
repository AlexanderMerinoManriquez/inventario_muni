import tkinter as tk

from config import BANNER_PATH, C


def build_header(self) -> None:
    header = tk.Frame(
        self.scroll_frame,
        bg=C["rojo"],
        bd=0,
        height=82,
    )
    header.pack(fill="x", pady=(0, 10))
    header.pack_propagate(False)

    tk.Frame(
        header,
        bg=C["rojo_dark"],
        height=3,
    ).pack(fill="x")

    inner = tk.Frame(
        header,
        bg=C["rojo"],
        padx=18,
        pady=7,
    )
    inner.pack(fill="both", expand=True)

    banner_loaded = False

    try:
        banner_img = tk.PhotoImage(file=BANNER_PATH)
        w = banner_img.width()

        if w > 230:
            banner_img = banner_img.subsample(max(1, round(w / 230)))

        lbl = tk.Label(
            inner,
            image=banner_img,
            bg=C["rojo"],
            bd=0,
        )
        lbl.image = banner_img
        lbl.pack(side="left", padx=(0, 18))
        banner_loaded = True

    except Exception:
        pass

    if not banner_loaded:
        tk.Label(
            inner,
            text="Municipalidad de Chillán",
            bg=C["rojo"],
            fg=C["blanco"],
            font=("Segoe UI", 17, "bold"),
        ).pack(side="left", padx=(0, 18))

    tk.Frame(
        inner,
        bg="#e8849a",
        width=1,
    ).pack(side="left", fill="y", padx=(0, 18))

    txt = tk.Frame(inner, bg=C["rojo"])
    txt.pack(side="left", fill="both", expand=True)

    tk.Label(
        txt,
        text="Sistema de Inventario de Equipos",
        bg=C["rojo"],
        fg="#ffe5ea",
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")

    tk.Label(
        txt,
        text="Registro y seguimiento de activos tecnológicos municipales",
        bg=C["rojo"],
        fg="#ffd6de",
        font=("Segoe UI", 8),
    ).pack(anchor="w", pady=(2, 0))