import requests
import tkinter as tk
import logging

from datetime import datetime
from tkinter import messagebox

from funciones.discos.main import obtener_discos_smart
from funciones.monitores import obtener_monitores
from funciones.impresoras import obtener_impresoras_activas
from funciones.permisos import admin
from utils.formato import formatear_capacidad
from utils.respaldo import guardar_respaldo
from ui.estilos import configurar_estilo
from utils.payload import construir_payload, validar_payload, normalizar_ram_gb
from ui.auto import mostrar_discos_en_auto_frame
from ui.layout import construir_interfaz
from ui.helpers import seccion, campo
from utils.rename_pc import generar_nombre_equipo, renombrar_equipo
from utils.logger import setup_logger
from utils.data_loader import cargar_funcionarios, cargar_usuarios_sistema

from ui.bloques import (
    crear_bloque_monitor,
    crear_bloque_impresora,
    renumerar_monitores,
    renumerar_impresoras,
)

from config import(
    CONFIG_PATH,
    ICON_PATH,
    CAMPOS_AUTO,
    C,
)
# ── Aplicación principal ───────────────────────────────────────────────────────
class InventarioApp:

    AUTO_FIELDS = [(c, e) for c, _, e in CAMPOS_AUTO]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sistema de Inventario — Municipalidad de Chillán")
        self.root.geometry("1200x900")
        self.root.minsize(1020, 740)
        self.root.configure(bg=C["gris_bg"])

        try:
            icon = tk.PhotoImage(file=ICON_PATH)
            self.root.iconphoto(True, icon)
        except Exception:
            pass

        # Estado interno
        self.fecha_hora_envio       = ""
        self.var_fecha_hora_visible = tk.StringVar()
        self.datos_auto             = {}
        self.discos_fisicos         = []
        self.monitores_detectados   = []
        self.monitores_vars         = []
        self.impresoras_vars        = []
        self.auto_entries           = {}
        self.discos_widgets         = []
        self.discos_entries         = []

        # Variables de formulario
        self.var_usuario             = tk.StringVar()
        self.var_rut_funcionario     = tk.StringVar()
        
        self.var_registrado_por         = tk.StringVar()
        self.var_rut_registrado_por     = tk.StringVar()
        
        self.var_departamento_manual = tk.StringVar()
        
        self.funcionarios_data = cargar_funcionarios() or []
        self.usuarios_sistema_data = cargar_usuarios_sistema() or []

        configurar_estilo()
        construir_interfaz(self)

        self._set_estado("● Preparando carga automática…", C["gris_sub"])
        self.root.after(300, self._cargar_datos_automaticos)
        
    def _seccion(self, parent, titulo, *, fill="x", expand=False, pady=(0, 14)):
        return seccion(parent, titulo, fill=fill, expand=expand, pady=pady)


    def _campo(self, parent, texto: str, variable: tk.StringVar,
            fila: int, width: int = 30, readonly: bool = False,
            obligatorio: bool = False):
        return campo(
            parent,
            texto,
            variable,
            fila,
            width=width,
            readonly=readonly,
            obligatorio=obligatorio,
        )

    def _editar_bloque_automatico(self) -> None:
        entries = [i["entry"] for i in self.auto_entries.values()] + self.discos_entries
        self._habilitar_grupo_generico(entries)
        
    def _bloquear_envio(self, bloquear: bool) -> None:
        estado = "disabled" if bloquear else "normal"

        if hasattr(self, "btn_registrar"):
            self.btn_registrar.config(state=estado)

    def _habilitar_grupo_generico(self, entries: list) -> None:
        for e in entries:
            e.config(state="normal")
        if entries:
            entries[0].focus_set()
            entries[0].icursor("end")

        def revisar(_=None):
            def bloquear():
                if self.root.focus_get() not in entries:
                    for e in entries:
                        e.config(state="readonly")
            self.root.after_idle(bloquear)

        for e in entries:
            e.unbind("<FocusOut>")
            e.unbind("<Return>")
            e.bind("<FocusOut>", revisar, add="+")
            e.bind("<Return>",   revisar, add="+")
                  
    def _on_funcionario_seleccionado(self, persona: dict) -> None:
        self.var_usuario.set(persona.get("nombre", ""))
        self.var_rut_funcionario.set(persona.get("rut", ""))
        self.var_departamento_manual.set(persona.get("departamento", ""))


    def _limpiar_funcionario(self) -> None:
        self.var_rut_funcionario.set("")
        self.var_departamento_manual.set("")


    def _on_registrado_por_seleccionado(self, persona: dict) -> None:
        self.var_rut_registrado_por.set(persona.get("rut", ""))
        self.var_registrado_por.set(persona.get("nombre", ""))


    def _limpiar_registrador(self) -> None:
        self.var_registrado_por.set("")
    #######################################
    def probar_nombre_equipo(self) -> None:
        nombre_sugerido = generar_nombre_equipo(
            self.var_departamento_manual.get(),
            self.var_usuario.get()
        )

        messagebox.showinfo(
            "Nombre sugerido",
            f"El nombre sugerido para este equipo es:\n\n{nombre_sugerido}"
        )
        
    def _crear_bloque_monitor(self, datos: dict = None) -> None:
        crear_bloque_monitor(self, datos)

    def _mostrar_estado_impresoras_vacio(self) -> None:
        if hasattr(self, "lbl_impresoras_vacio"):
            self.lbl_impresoras_vacio.pack(fill="x", padx=10, pady=(0, 8))

    def _ocultar_estado_impresoras_vacio(self) -> None:
        if hasattr(self, "lbl_impresoras_vacio"):
            self.lbl_impresoras_vacio.pack_forget()

    def _mostrar_estado_impresoras_vacio(self) -> None:
        self.impresoras_vars.clear()

        if hasattr(self, "impresoras_container"):
            for child in self.impresoras_container.winfo_children():
                child.destroy()

            self.impresoras_container.pack_forget()

        if hasattr(self, "lbl_impresoras_vacio"):
            self.lbl_impresoras_vacio.pack(fill="x", padx=10, pady=(0, 8))


    def _ocultar_estado_impresoras_vacio(self) -> None:
        if hasattr(self, "lbl_impresoras_vacio"):
            self.lbl_impresoras_vacio.pack_forget()

        if hasattr(self, "impresoras_container"):
            self.impresoras_container.pack(fill="x", padx=10, pady=(0, 6))


    def _crear_bloque_impresora(self, datos: dict = None) -> None:
        self._ocultar_estado_impresoras_vacio()
        crear_bloque_impresora(self, datos)

    def _renumerar_monitores(self) -> None:
        renumerar_monitores(self)

    def _renumerar_impresoras(self) -> None:
        renumerar_impresoras(self)

    def _habilitar_grupo(self, entries: dict) -> None:
        lista = list(entries.values())
        for e in lista:
            e.config(state="normal")
        if lista:
            lista[0].focus_set()
            lista[0].icursor("end")

        def revisar(_=None):
            def bloquear():
                if self.root.focus_get() not in lista:
                    for e in lista:
                        e.config(state="readonly")
            self.root.after_idle(bloquear)

        for e in lista:
            e.unbind("<FocusOut>")
            e.unbind("<Return>")
            e.bind("<FocusOut>", revisar, add="+")
            e.bind("<Return>",   revisar, add="+")

    # ── Reloj ─────────────────────────────────────────────────────────────────
    def _actualizar_reloj(self) -> None:
        self.var_fecha_hora_visible.set(datetime.now().strftime("%Y-%m-%d   %H:%M:%S"))
        self.root.after(1000, self._actualizar_reloj)

    def _get_auto(self, clave: str) -> str:
        item = self.auto_entries.get(clave)
        return item["var"].get().strip() if item else ""
    
    # ── Carga automática ───────────────────────────────────────────────────────
    def _cargar_datos_automaticos(self) -> None:
        self._set_estado("Cargando datos automáticos…", C["gris_sub"])
        self.root.update_idletasks()
        errores = []

        try:
            admin()
        except Exception as e:
            errores.append(f"admin(): {e}")

        for clave, fn, _ in CAMPOS_AUTO:
            try:
                valor = fn()
            except Exception as e:
                valor = "ERROR"
                errores.append(f"{clave}: {e}")
                logging.error(f"Error en {clave}", exc_info=True)

            if clave == "ram":
                ram_normalizada = normalizar_ram_gb(valor)
                valor = f"{int(ram_normalizada)} GB" if ram_normalizada else formatear_capacidad(valor)

            self.datos_auto[clave] = valor
            self.auto_entries[clave]["var"].set(str(valor))

        try:
            self.discos_fisicos = obtener_discos_smart()
        except Exception as e:
            self.discos_fisicos = []
            errores.append(f"discos: {e}")
            logging.error("Error obteniendo discos", exc_info=True)

        try:
            self.monitores_detectados = obtener_monitores()
        except Exception as e:
            self.monitores_detectados = []
            errores.append(f"monitores: {e}")
            logging.error("Error obteniendo monitores", exc_info=True)

        mostrar_discos_en_auto_frame(self)
        self._agregar_observacion_discos_secundarios()

        for m in self.monitores_detectados:
            self._crear_bloque_monitor(m)
        if not self.monitores_vars:
            self._crear_bloque_monitor()

        try:
            impresoras = obtener_impresoras_activas()
        except Exception as e:
            impresoras = []
            errores.append(f"impresoras: {e}")
            logging.error("Error obteniendo impresoras", exc_info=True)

        for imp in impresoras:
            self._crear_bloque_impresora(imp)

        if not self.impresoras_vars:
            self._mostrar_estado_impresoras_vacio()

        if errores:
            self._set_estado("● Carga parcial con errores", C["amarillo"])
            messagebox.showwarning(
                "Carga parcial",
                "La ventana abrió, pero algunos datos automáticos fallaron:\n\n"
                + "\n".join(errores),
            )
        else:
            self._set_estado("● Datos automáticos cargados ✓", C["verde"])


    def _agregar_observacion_discos_secundarios(self) -> None:
        if not hasattr(self, "txt_observaciones"):
            return

        discos = self.discos_fisicos or []

        if len(discos) <= 1:
            return

        def capacidad_numero(disco):
            capacidad = str(disco.get("capacidad", "") or "")
            capacidad = capacidad.upper().replace("GB", "").strip()

            try:
                return float(capacidad)
            except ValueError:
                return 0

        discos_ordenados = sorted(
            discos,
            key=lambda d: (
                str(d.get("tipo", "")).upper() != "SSD",
                -capacidad_numero(d),
            ),
        )

        secundarios = discos_ordenados[1:]

        textos = []

        for disco in secundarios:
            tipo = str(disco.get("tipo", "disco") or "disco").upper()
            capacidad = str(disco.get("capacidad", "") or "").strip()

            if capacidad:
                textos.append(
                    f"Este equipo cuenta con otro disco de almacenamiento {tipo} de capacidad {capacidad}."
                )
            else:
                textos.append(
                    f"Este equipo cuenta con otro disco de almacenamiento {tipo}."
                )

        if not textos:
            return

        texto_actual = self.txt_observaciones.get("1.0", "end").strip()
        texto_nuevo = " ".join(textos)

        if texto_nuevo.lower() in texto_actual.lower():
            return

        if texto_actual:
            self.txt_observaciones.insert("end", "\n" + texto_nuevo)
        else:
            self.txt_observaciones.insert("1.0", texto_nuevo)

    def _set_estado(self, texto: str, color: str) -> None:
        self.lbl_estado.config(text=texto, foreground=color)

    # ── Envío ──────────────────────────────────────────────────────────────────
    def enviar_datos(self) -> None:
        payload = construir_payload(self)
        ok, faltantes = validar_payload(payload)

        if not self.buscador_funcionario.es_seleccion_valida():
            faltantes.append("Funcionario válido seleccionado desde la lista")

        if not self.buscador_registrado_por.es_seleccion_valida():
            faltantes.append("Registrador válido seleccionado desde la lista")

        if faltantes:
            messagebox.showwarning(
                "Faltan datos",
                "Completa estos campos obligatorios:\n\n— " + "\n— ".join(faltantes),
            )
            return

        if not messagebox.askyesno(
            "Confirmar registro",
            "¿Confirmas el envío de este inventario?"
        ):
            return

        self._bloquear_envio(True)

        try:
            try:
                with open(CONFIG_PATH, encoding="utf-8") as f:
                    url = f.read().strip()

                if not url:
                    messagebox.showerror(
                        "Configuración incompleta",
                        "config.txt está vacío. Debes configurar la URL de la API antes de registrar."
                    )
                    self._set_estado("● URL no configurada", C["rojo"])
                    return

            except Exception as e:
                messagebox.showerror(
                    "Error de configuración",
                    f"No se encontró config.txt\n\n{e}"
                )
                return

            self._set_estado("● Enviando datos…", C["rojo"])
            self.root.update_idletasks()

            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers={"ngrok-skip-browser-warning": "true"},
                    timeout=60,
                )
                
                try:
                    rj = resp.json()
                except Exception:
                    logging.error("Respuesta del servidor no es JSON válido", exc_info=True)

                    ruta = guardar_respaldo(payload, "RESPUESTA_NO_JSON", resp.text)
                    messagebox.showerror(
                        "Respuesta inválida",
                        f"El servidor no devolvió JSON válido.\n\nRespaldo en:\n{ruta}"
                    )
                    self._set_estado("● Error — respuesta no JSON", C["rojo"])
                    return

                if rj.get("success") is True:
                    messagebox.showinfo(
                        "Registro exitoso",
                        f"Equipo registrado correctamente.\n\n{rj.get('message', '')}"
                    )

                    self._set_estado("● Registrado correctamente ✓", C["verde"])

                    nombre_sugerido = generar_nombre_equipo(
                        self.var_departamento_manual.get(),
                        self.var_usuario.get()
                    )

                    if messagebox.askyesno(
                        "Renombrar equipo",
                        f"Nombre sugerido: {nombre_sugerido}\n\n¿Deseas renombrar este equipo?"
                    ):
                        ok_rename, msg = renombrar_equipo(nombre_sugerido)

                        if ok_rename:
                            messagebox.showinfo("Equipo renombrado", msg)
                        else:
                            messagebox.showerror("Error al renombrar", msg)
                else:
                    ruta = guardar_respaldo(payload, "ERROR_SERVIDOR", resp.text)
                    messagebox.showerror(
                        "Error del servidor",
                        f"Motivo: {rj.get('message', 'Sin mensaje')}\n\nRespaldo:\n{ruta}"
                    )
                    self._set_estado("● Error del servidor", C["rojo"])

            except requests.exceptions.RequestException as e:
                logging.error("Error de conexión al enviar datos", exc_info=True)
                ruta = guardar_respaldo(payload, "ERROR_ENVIO", str(e))
                messagebox.showerror(
                    "Error de conexión",
                    f"No se pudo conectar con el servidor.\n\n{e}\n\nRespaldo:\n{ruta}"
                )
                self._set_estado("● Sin conexión", C["rojo"])

        finally:
            self._bloquear_envio(False)


# ── Punto de entrada ───────────────────────────────────────────────────────────
def main() -> None:
    try:
        setup_logger()
        root = tk.Tk()
        InventarioApp(root)
        root.mainloop()
    except Exception:
        import traceback
        print("ERROR AL INICIAR:\n", traceback.format_exc())
        input("Presiona ENTER para salir...")


if __name__ == "__main__":
    main()