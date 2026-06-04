import ctypes
import sys
import time


def admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _mostrar_error_permisos() -> None:
    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title("SMART — Error de permisos")
        root.resizable(False, False)
        root.configure(bg="#ffffff")

        root.update_idletasks()
        ancho, alto = 420, 200
        x = (root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (root.winfo_screenheight() // 2) - (alto // 2)
        root.geometry(f"{ancho}x{alto}+{x}+{y}")

        marco = tk.Frame(root, bg="#ffffff", padx=24, pady=20)
        marco.pack(fill="both", expand=True)

        encabezado = tk.Frame(marco, bg="#ffffff")
        encabezado.pack(fill="x", pady=(0, 10))

        tk.Label(
            encabezado,
            text="⚠",
            bg="#ffffff",
            fg="#C8102E",
            font=("Segoe UI", 22),
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            encabezado,
            text="Se requieren permisos de administrador",
            bg="#ffffff",
            fg="#1a2035",
            font=("Segoe UI", 11, "bold"),
            wraplength=320,
            justify="left",
        ).pack(side="left")

        tk.Label(
            marco,
            text=(
                "El sistema de inventario necesita ejecutarse como\n"
                "administrador para leer correctamente los datos del equipo.\n\n"
                "Por favor, cierra esta ventana y ejecuta el programa\n"
                "haciendo clic derecho → \"Ejecutar como administrador\"."
            ),
            bg="#ffffff",
            fg="#4a5568",
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        ttk.Button(
            marco,
            text="Cerrar",
            command=root.destroy,
        ).pack(anchor="e")

        root.mainloop()

    except Exception:
        print("Hubo un error en los permisos de administrador de SMART")
        print("El programa se cerrará en 5 segundos...")
        time.sleep(5)


if not admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1,
        )
    except Exception:
        _mostrar_error_permisos()

    sys.exit()

print("Smart ejecutándose con privilegios de administrador")