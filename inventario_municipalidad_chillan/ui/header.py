import tkinter as tk

from config import BANNER_PATH, C

def build_header(self) -> None:
    header = tk.Frame(self.scroll_frame, bg=C["rojo"], bd=0)
    header.pack(fill="x", pady=(0, 22))
    tk.Frame(header, bg=C["rojo_dark"], height=4).pack(fill="x")
    inner = tk.Frame(header, bg=C["rojo"], padx=20, pady=10)
    inner.pack(fill="x")
    banner_loaded = False
    try:
        banner_img = tk.PhotoImage(file=BANNER_PATH)
        w = banner_img.width()
        if w > 260:
            banner_img = banner_img.subsample(max(1, round(w / 260)))
        lbl = tk.Label(inner, image=banner_img, bg=C["rojo"], bd=0)
        lbl.image = banner_img
        lbl.pack(side="left", padx=(0, 20))
        banner_loaded = True
    except Exception:
        pass
    if not banner_loaded:
        tk.Label(inner, text="Municipalidad de Chillán",
                 bg=C["rojo"], fg=C["blanco"],
                 font=("Segoe UI", 18, "bold")).pack(side="left")
    tk.Frame(inner, bg="#e8849a", width=1).pack(side="left", fill="y", padx=(0, 20))
    txt = tk.Frame(inner, bg=C["rojo"])
    txt.pack(side="left", fill="y")
    tk.Label(txt, text="Sistema de Inventario de Equipos",
             bg=C["rojo"], fg="#ffe5ea",
             font=("Segoe UI", 14, "bold")).pack(anchor="w")
    tk.Label(txt, text="Registro y seguimiento de activos tecnológicos municipales",
             bg=C["rojo"], fg="#ffd6de",
             font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 0))