import logging
import tkinter as tk

from datetime import datetime
from tkinter import messagebox

from config import CONFIG_PATH, ICON_PATH, CAMPOS_AUTO, C

from funciones.discos.main import obtener_discos_smart
from funciones.monitores import obtener_monitores
from funciones.impresoras import obtener_impresoras_activas
from funciones.tipo_equipo import detectar_tipo_equipo

from utils.formato import formatear_capacidad
from utils.respaldo import guardar_respaldo
from utils.api_cliente import leer_url_api, enviar_payload_api
from utils.payload import construir_payload, validar_payload, normalizar_ram_gb
from utils.observaciones import (
    agregar_observacion_discos_secundarios,
    agregar_observacion_pantallas_integradas,
)
from utils.logger import setup_logger, limpiar_logs_antiguos
from utils.rut import formatear_rut
from utils.data_loader import cargar_funcionarios, cargar_usuarios_sistema, cargar_departamentos

from ui.estilos import configurar_estilo
from ui.auto import mostrar_discos_en_auto_frame
from ui.layout import construir_interfaz
from ui.helpers import seccion, campo
from ui.validacion import limpiar_validacion_visual, marcar_validacion_visual, set_entry_normal
from ui.bloques import (
    crear_bloque_monitor, crear_bloque_impresora,
    renumerar_monitores, renumerar_impresoras,
)


class InventarioApp:
    AUTO_FIELDS = [(clave, etiqueta) for clave, _, etiqueta in CAMPOS_AUTO]

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

        self.fecha_hora_envio = ""
        self.var_fecha_hora_visible = tk.StringVar()

        self.datos_auto = {}
        self.discos_fisicos = []
        self.monitores_detectados = []
        self.tipo_equipo_fisico = "DESCONOCIDO"

        self.monitores_vars = []
        self.impresoras_vars = []
        self.auto_entries = {}
        self.discos_widgets = []
        self.discos_entries = []

        self.var_usuario = tk.StringVar()
        self.var_rut_funcionario = tk.StringVar()
        self.var_departamento_funcionario = tk.StringVar()
        self.var_nombre_registrador = tk.StringVar()
        self.var_rut_registrador = tk.StringVar()

        self.id_funcionario_seleccionado = None
        self.id_registrador_seleccionado = None
        self.id_departamento_seleccionado = None

        self.funcionarios_data = cargar_funcionarios() or []
        self.usuarios_sistema_data = cargar_usuarios_sistema() or []
        self.departamentos_data = cargar_departamentos() or []

        configurar_estilo()
        construir_interfaz(self)
        self._instalar_formateo_rut()

        self._set_estado("● Preparando carga automática…", C["gris_sub"])
        self.root.after(300, self._cargar_datos_automaticos)

    # ── Helpers de interfaz ───────────────────────────────────────────────────
    def _seccion(self, parent, titulo, *, fill="x", expand=False, pady=(0, 14)):
        return seccion(parent, titulo, fill=fill, expand=expand, pady=pady)

    def _campo(self, parent, texto, variable, fila, width=30, readonly=False, obligatorio=False):
        return campo(parent, texto, variable, fila, width=width, readonly=readonly, obligatorio=obligatorio)

    def _set_estado(self, texto: str, color: str) -> None:
        if hasattr(self, "lbl_estado"):
            self.lbl_estado.config(text=texto, foreground=color)

    def _bloquear_envio(self, bloquear: bool) -> None:
        if hasattr(self, "btn_registrar"):
            self.btn_registrar.config(state="disabled" if bloquear else "normal")

    # ── Validación de RUT ─────────────────────────────────────────────────────
    def _entrada_rut_permitida(self, valor_propuesto: str) -> bool:
        caracteres = []
        for c in str(valor_propuesto or ""):
            if c.isdigit():
                caracteres.append(c)
            elif c.upper() == "K":
                caracteres.append("K")
            elif c in ".- ":
                continue
            else:
                return False
        if len(caracteres) > 9:
            return False
        if "K" in caracteres[:-1]:
            return False
        return True

    def _bind_formato_rut(self, entry, variable, variable_visible=None) -> None:
        if not entry:
            return

        vcmd = (self.root.register(self._entrada_rut_permitida), "%P")
        entry.configure(validate="key", validatecommand=vcmd)

        def aplicar_formato(_=None):
            var_visible = variable_visible or variable
            valor = formatear_rut(var_visible.get()) or ""
            if variable_visible is not None and variable_visible.get() != valor:
                variable_visible.set(valor)
            if variable.get() != valor:
                variable.set(valor)
            entry.icursor(tk.END)

        entry.bind("<KeyRelease>", lambda e: self.root.after_idle(aplicar_formato), add="+")
        entry.bind("<<Paste>>", lambda e: self.root.after_idle(aplicar_formato), add="+")

    def _instalar_formateo_rut(self) -> None:
        self._bind_formato_rut(self.entry_rut_funcionario, self.var_rut_funcionario)
        self._bind_formato_rut(
            self.buscador_registrador.entry,
            self.var_rut_registrador,
            self.buscador_registrador.var_buscar,
        )

    # ── Edición de campos ──────────────────────────────────────────────────────
    def _habilitar_grupo_generico(self, entries: list) -> None:
        entries = [e for e in entries if e]
        for entry in entries:
            set_entry_normal(entry)
            entry.config(state="normal")
        if entries:
            entries[0].focus_set()
            entries[0].icursor("end")

        def revisar(_=None):
            def bloquear():
                if self.root.focus_get() not in entries:
                    for entry in entries:
                        entry.config(state="readonly")
            self.root.after_idle(bloquear)

        for entry in entries:
            entry.unbind("<FocusOut>")
            entry.unbind("<Return>")
            entry.bind("<FocusOut>", revisar, add="+")
            entry.bind("<Return>", revisar, add="+")

    def _habilitar_grupo(self, entries: dict) -> None:
        self._habilitar_grupo_generico(list(entries.values()))

    def _editar_bloque_automatico(self) -> None:
        entries = [
            item["entry"]
            for item in self.auto_entries.values()
            if item.get("entry")
        ] + self.discos_entries
        self._habilitar_grupo_generico(entries)

    # ── Buscadores ─────────────────────────────────────────────────────────────
    def _on_funcionario_seleccionado(self, persona: dict) -> None:
        rut = formatear_rut(persona.get("rut", "")) or ""
        self.id_funcionario_seleccionado = persona.get("id")
        self.var_usuario.set(persona.get("nombre", ""))
        self.var_rut_funcionario.set(rut)
        for entry in (
            getattr(getattr(self, "buscador_funcionario", None), "entry", None),
            getattr(self, "entry_rut_funcionario", None),
        ):
            set_entry_normal(entry)

    def _limpiar_funcionario(self) -> None:
        self.id_funcionario_seleccionado = None
        self.var_rut_funcionario.set("")

    def _on_departamento_seleccionado(self, departamento: dict) -> None:
        self.id_departamento_seleccionado = departamento.get("id")
        self.var_departamento_funcionario.set(departamento.get("nombre", ""))
        set_entry_normal(getattr(getattr(self, "buscador_departamento", None), "entry", None))

    def _limpiar_departamento(self) -> None:
        self.id_departamento_seleccionado = None
        self.var_departamento_funcionario.set("")

    def _on_registrador_seleccionado(self, persona: dict) -> None:
        rut = formatear_rut(persona.get("rut", "")) or ""
        self.id_registrador_seleccionado = persona.get("id")
        self.var_rut_registrador.set(rut)
        self.var_nombre_registrador.set(persona.get("nombre", ""))
        if hasattr(self, "buscador_registrador"):
            self.buscador_registrador._set_valor_sin_trace(rut)
            self.buscador_registrador._marcar_seleccionado(True)
            self.buscador_registrador._ocultar_lista()
        for entry in (
            getattr(getattr(self, "buscador_registrador", None), "entry", None),
            getattr(self, "entry_nombre_registrador", None),
        ):
            set_entry_normal(entry)

    def _limpiar_registrador(self) -> None:
        self.id_registrador_seleccionado = None
        self.var_nombre_registrador.set("")

    # ── Estados vacíos ─────────────────────────────────────────────────────────
    def _mostrar_estado_monitores_vacio(self) -> None:
        self.monitores_vars.clear()
        if hasattr(self, "monitores_container"):
            for child in self.monitores_container.winfo_children():
                child.destroy()
            self.monitores_container.pack_forget()
        if hasattr(self, "lbl_monitores_vacio"):
            self.lbl_monitores_vacio.pack(fill="x", padx=10, pady=(0, 8))

    def _ocultar_estado_monitores_vacio(self) -> None:
        if hasattr(self, "lbl_monitores_vacio"):
            self.lbl_monitores_vacio.pack_forget()
        if hasattr(self, "monitores_container"):
            self.monitores_container.pack(fill="x", padx=10, pady=(0, 6))

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

    # ── Bloques ────────────────────────────────────────────────────────────────
    def _crear_bloque_monitor(self, datos: dict = None) -> None:
        self._ocultar_estado_monitores_vacio()
        crear_bloque_monitor(self, datos)

    def _crear_bloque_impresora(self, datos: dict = None) -> None:
        self._ocultar_estado_impresoras_vacio()
        crear_bloque_impresora(self, datos)

    def _renumerar_monitores(self) -> None:
        renumerar_monitores(self)

    def _renumerar_impresoras(self) -> None:
        renumerar_impresoras(self)

    # ── Reloj ──────────────────────────────────────────────────────────────────
    def _actualizar_reloj(self) -> None:
        self.var_fecha_hora_visible.set(datetime.now().strftime("%Y-%m-%d   %H:%M:%S"))
        self.root.after(1000, self._actualizar_reloj)

    # ── Datos automáticos ──────────────────────────────────────────────────────
    def _get_auto(self, clave: str) -> str:
        item = self.auto_entries.get(clave)
        return item["var"].get().strip() if item else ""

    def _cargar_datos_automaticos(self) -> None:
        self._set_estado("Cargando datos automáticos…", C["gris_sub"])
        self.root.update_idletasks()

        errores = []

        try:
            self.tipo_equipo_fisico = detectar_tipo_equipo()
        except Exception as e:
            self.tipo_equipo_fisico = "DESCONOCIDO"
            errores.append(f"tipo_equipo: {e}")
            logging.error("Error detectando tipo físico del equipo", exc_info=True)

        for clave, fn, _ in CAMPOS_AUTO:
            try:
                valor = fn()
            except Exception as e:
                valor = "ERROR"
                errores.append(f"{clave}: {e}")
                logging.error("Error en %s", clave, exc_info=True)

            if clave == "ram":
                ram_normalizada = normalizar_ram_gb(valor)
                valor = (
                    f"{int(ram_normalizada)} GB"
                    if ram_normalizada
                    else formatear_capacidad(valor)
                )

            self.datos_auto[clave] = valor
            if clave in self.auto_entries:
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
        agregar_observacion_discos_secundarios(self)

        monitores_integrados = [m for m in self.monitores_detectados if m.get("es_pantalla_integrada")]
        monitores_externos = [m for m in self.monitores_detectados if not m.get("es_pantalla_integrada")]

        if monitores_integrados:
            agregar_observacion_pantallas_integradas(self, monitores_integrados)

        for monitor in monitores_externos:
            self._crear_bloque_monitor(monitor)

        if not self.monitores_vars:
            self._mostrar_estado_monitores_vacio()

        try:
            impresoras = obtener_impresoras_activas()
        except Exception as e:
            impresoras = []
            errores.append(f"impresoras: {e}")
            logging.error("Error obteniendo impresoras", exc_info=True)

        for impresora in impresoras:
            self._crear_bloque_impresora(impresora)

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

    # ── Envío ──────────────────────────────────────────────────────────────────
    def enviar_datos(self) -> None:
        for buscador in (
            getattr(self, "buscador_departamento", None),
            getattr(self, "buscador_funcionario", None),
            getattr(self, "buscador_registrador", None),
        ):
            if buscador:
                buscador.validar_o_limpiar()

        limpiar_validacion_visual(self)
        self.fecha_hora_envio = datetime.now().strftime("%Y-%m-%d %H:%M")

        payload = construir_payload(self)
        ok, faltantes = validar_payload(payload)
        marcar_validacion_visual(self, payload)

        if faltantes:
            messagebox.showwarning(
                "Faltan datos",
                "Completa estos campos obligatorios:\n\n— " + "\n— ".join(faltantes),
            )
            return

        if not messagebox.askyesno("Confirmar registro", "¿Confirmas el envío de este inventario?"):
            return

        self._bloquear_envio(True)
        try:
            url, error = leer_url_api(CONFIG_PATH)
            if error:
                messagebox.showerror("Error de configuración", error)
                self._set_estado("● URL no configurada", C["rojo"])
                return
            self._enviar_payload(url, payload)
        finally:
            self._bloquear_envio(False)

    def _enviar_payload(self, url: str, payload: dict) -> None:
        self._set_estado("● Enviando datos…", C["rojo"])
        self.root.update_idletasks()

        resultado = enviar_payload_api(url, payload)

        if resultado.get("ok") is True:
            self._registro_exitoso(resultado.get("data", {}))
            return

        tipo = resultado.get("tipo")
        detalle = resultado.get("detalle", "")
        mensaje = resultado.get("mensaje", "Error desconocido")

        if tipo == "conexion":
            ruta = guardar_respaldo(payload, "ERROR_ENVIO", detalle)
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar con el servidor.\n\n{mensaje}\n\nRespaldo:\n{ruta}",
            )
            self._set_estado("● Sin conexión", C["rojo"])
            return

        if tipo == "respuesta_no_json":
            ruta = guardar_respaldo(payload, "RESPUESTA_NO_JSON", detalle)
            messagebox.showerror(
                "Respuesta inválida",
                f"El servidor no devolvió JSON válido.\n\nRespaldo en:\n{ruta}",
            )
            self._set_estado("● Error — respuesta no JSON", C["rojo"])
            return

        ruta = guardar_respaldo(payload, "ERROR_SERVIDOR", detalle)
        messagebox.showerror("Error del servidor", f"Motivo: {mensaje}\n\nRespaldo:\n{ruta}")
        self._set_estado("● Error del servidor", C["rojo"])

    def _registro_exitoso(self, respuesta_json: dict) -> None:
        mensaje = (
            respuesta_json.get("message")
            or respuesta_json.get("mensaje")
            or "Registro guardado correctamente."
        )
        datos = respuesta_json.get("datos") or respuesta_json.get("data") or {}
        activos = datos.get("activos_procesados") or []
        asignaciones = datos.get("asignaciones") or []
        advertencias = datos.get("advertencias") or []

        resumen = f"{mensaje}\n"

        if activos:
            resumen += "\nActivos procesados:"
            for activo in activos:
                if isinstance(activo, dict):
                    tipo = activo.get("tipo", "ACTIVO")
                    linea = f"\n- {tipo}: {activo.get('accion', 'procesado')}"
                    if activo.get("id_activo"):
                        linea += f" | ID: {activo['id_activo']}"
                    if activo.get("codigo_inventario"):
                        linea += f" | Código: {activo['codigo_inventario']}"
                    if activo.get("numero_de_serie"):
                        linea += f" | Serie: {activo['numero_de_serie']}"
                    resumen += linea
                else:
                    resumen += f"\n- {activo}"
        else:
            resumen += "\nActivos procesados: 0"

        if asignaciones:
            resumen += "\n\nAsignaciones procesadas:"
            for asignacion in asignaciones:
                if isinstance(asignacion, dict):
                    linea = f"\n- {asignacion.get('tipo', 'ACTIVO')}"
                    if asignacion.get("id_activo"):
                        linea += f" | ID activo: {asignacion['id_activo']}"
                    if asignacion.get("id_asignacion"):
                        linea += f" | ID asignación: {asignacion['id_asignacion']}"
                    resumen += linea
                else:
                    resumen += f"\n- {asignacion}"
        else:
            resumen += "\n\nAsignaciones procesadas: 0"

        if advertencias:
            resumen += "\n\nAdvertencias:"
            for adv in advertencias:
                if isinstance(adv, dict):
                    linea = f"\n- {adv.get('tipo', 'ACTIVO')}: {adv.get('mensaje', 'Sin detalle')}"
                    if adv.get("id_activo"):
                        linea += f" | ID: {adv['id_activo']}"
                    resumen += linea
                else:
                    resumen += f"\n- {adv}"
            messagebox.showwarning("Registro con advertencias", resumen)
            self._set_estado("● Registrado con advertencias", C["amarillo"])
        else:
            messagebox.showinfo("Registro exitoso", resumen)
            self._set_estado("● Registrado correctamente ✓", C["verde"])


def main() -> None:
    try:
        setup_logger()
        limpiar_logs_antiguos()

        root = tk.Tk()
        InventarioApp(root)
        root.mainloop()

    except Exception:
        logging.exception("Error crítico al iniciar la aplicación")

        try:
            messagebox.showerror(
                "Error crítico",
                "Ocurrió un error al iniciar el sistema.\n\n"
                "Revisa el archivo de log para más detalles.",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
    
