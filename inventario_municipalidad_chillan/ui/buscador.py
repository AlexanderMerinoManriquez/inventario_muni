import tkinter as tk
from tkinter import ttk
 
from config import C
 
 
class BuscadorAutocomplete(tk.Frame):
    MIN_CHARS = 2
    MAX_RESULTADOS = 8
 
    def __init__(
        self,
        parent,
        datos,
        variable,
        campo_busqueda="nombre",
        campo_valor="nombre",
        campos_extra_busqueda=None,
        formato_resultado=None,
        on_select=None,
        on_clear=None,
        permitir_manual=False,
        **kwargs,
    ):
        super().__init__(parent, bg=C["gris_panel"])
 
        self.datos = datos or []
        self.variable = variable
        self.campo_busqueda = campo_busqueda
        self.campo_valor = campo_valor
        self.campos_extra_busqueda = campos_extra_busqueda or []
        self.formato_resultado = formato_resultado or self._formato_default
        self.on_select = on_select
        self.on_clear = on_clear
        self.permitir_manual = permitir_manual
        self.resultados = []
        self._seleccionado = False
        self._trace_id = None
 
        self.var_buscar = tk.StringVar(value=variable.get())
 
        # ── Barra de búsqueda ──────────────────────────────────────────────────
        barra = ttk.Frame(self)
        barra.pack(fill="x")
 
        self._lbl_icono = tk.Label(
            barra,
            text="⌕",
            bg=C["gris_panel"],
            fg=C["gris_sub"],
            font=("Segoe UI", 11, "bold"),
        )
        self._lbl_icono.pack(side="left", padx=(0, 4))
 
        self.entry = ttk.Entry(barra, textvariable=self.var_buscar, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
        # ── Lista desplegable ──────────────────────────────────────────────────
        self.lista = tk.Listbox(
            self,
            height=0,
            font=("Segoe UI", 9),
            activestyle="none",
            bg=C["blanco"],
            fg=C["texto"],
            selectbackground=C["rojo"],
            selectforeground=C["blanco"],
            borderwidth=1,
            relief="solid",
        )
        self.lista.pack(fill="x", pady=(3, 0))
        self.lista.pack_forget()
 
        # ── Bindings ───────────────────────────────────────────────────────────
        self._activar_trace()
        self.lista.bind("<ButtonPress-1>", self._seleccionar_click)
        self.lista.bind("<Return>",          lambda e: self._seleccionar())
        self.entry.bind("<Return>",          lambda e: self._seleccionar_primero())
        self.entry.bind("<Escape>",          lambda e: self._ocultar_lista())
        self.entry.bind("<Down>",            lambda e: self._mover_lista(1))
        self.entry.bind("<Up>",              lambda e: self._mover_lista(-1))
        self.lista.bind("<Down>",            lambda e: self._mover_lista(1))
        self.lista.bind("<Up>",              lambda e: self._mover_lista(-1))
        # Al perder foco: si no hay selección válida, limpiar
        self.entry.bind("<FocusOut>",        lambda e: self.after(150, self._validar_al_salir))
 
    # ── Normalización ──────────────────────────────────────────────────────────
    def _normalizar(self, texto: str) -> str:
        tabla = str.maketrans("áéíóúÁÉÍÓÚüÜñÑ", "aeiouAEIOUuUnN")
        texto = str(texto or "").translate(tabla).lower()

        return (
            texto
            .replace(".", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )
    def _formato_default(self, item: dict) -> str:
        rut = str(item.get("rut", "")).strip()
        nombre = str(item.get("nombre", "")).strip()
        return f"{rut} — {nombre}" if rut and nombre else nombre or rut
 
    def _texto_busqueda(self, item: dict) -> str:
        campos = [self.campo_busqueda, *self.campos_extra_busqueda]
        return " ".join(str(item.get(c, "")) for c in campos)
 
    # ── Estado visual ──────────────────────────────────────────────────────────
    def _marcar_seleccionado(self, ok: bool) -> None:
        self._seleccionado = ok
    # ── Control de trace ──────────────────────────────────────────────────────
    def _activar_trace(self) -> None:
        if self._trace_id is None:
            self._trace_id = self.var_buscar.trace_add(
                "write",
                lambda *_: self._on_escribir()
            )
            
    def _desactivar_trace(self) -> None:
        if self._trace_id is None:
            return

        try:
            self.var_buscar.trace_remove("write", self._trace_id)
        except tk.TclError:
            pass
        finally:
            self._trace_id = None

    def _set_valor_sin_trace(self, valor: str) -> None:
        self._desactivar_trace()

        try:
            self.var_buscar.set(valor)
            self.variable.set(valor)
        finally:
            self._activar_trace()
    # ── Eventos de escritura ───────────────────────────────────────────────────
    def _on_escribir(self):
        """Llamado cada vez que cambia el texto. Marca como no-seleccionado."""
        self._marcar_seleccionado(False)
        self._filtrar()
 
    def _filtrar(self):
        valor_original = self.var_buscar.get().strip()
        texto = self._normalizar(valor_original)
 
        if not valor_original:
            self.variable.set("")
            self.resultados = []
            self._ocultar_lista()
            if self.on_clear:
                self.on_clear()
            return
 
        self.variable.set(valor_original)
 
        if len(texto) < self.MIN_CHARS:
            self._ocultar_lista()
            return
 
        palabras = texto.split()
        coinciden = [
            item for item in self.datos
            if all(p in self._normalizar(self._texto_busqueda(item)) for p in palabras)
        ]
        empiezan = [
            item for item in coinciden
            if self._normalizar(str(item.get(self.campo_busqueda, ""))).startswith(texto)
        ]
        resto = [item for item in coinciden if item not in empiezan]
        self.resultados = (empiezan + resto)[:self.MAX_RESULTADOS]
 
        self.lista.delete(0, tk.END)
        if not self.resultados:
            self._ocultar_lista()
            return
 
        for item in self.resultados:
            self.lista.insert(tk.END, self.formato_resultado(item))
 
        self.lista.config(height=len(self.resultados))
        self.lista.pack(fill="x", pady=(3, 0))
 
    # ── Navegación con teclado ─────────────────────────────────────────────────
    def _mover_lista(self, delta: int) -> str:
        if not self.resultados:
            self._filtrar()

        if not self.resultados:
            return "break"

        focus = self.winfo_toplevel().focus_get()
        size = self.lista.size()
        actual = self.lista.curselection()

        if focus == self.entry and delta < 0:
            self.entry.icursor(tk.END)
            return "break"

        if focus == self.lista and delta < 0 and (not actual or actual[0] <= 0):
            self.lista.selection_clear(0, tk.END)
            self.entry.focus_set()
            self.entry.icursor(tk.END)
            return "break"

        if focus == self.entry and delta > 0:
            idx = 0
        elif actual:
            idx = actual[0] + delta
        else:
            idx = 0 if delta > 0 else size - 1

        idx = max(0, min(idx, size - 1))

        self.lista.selection_clear(0, tk.END)
        self.lista.selection_set(idx)
        self.lista.activate(idx)
        self.lista.see(idx)
        self.lista.focus_set()

        return "break"
    # ── Selección con mouse ───────────────────────────────────────────────────
    def _seleccionar_click(self, event):
        if not self.resultados:
            return "break"

        idx = self.lista.nearest(event.y)

        if 0 <= idx < len(self.resultados):
            self.lista.selection_clear(0, tk.END)
            self.lista.selection_set(idx)
            self._seleccionar()

        return "break"
    # ── Selección ─────────────────────────────────────────────────────────────
    def _seleccionar_primero(self):
        if self.lista.size() > 0:
            self.lista.selection_clear(0, tk.END)
            self.lista.selection_set(0)
            self._seleccionar()
            return "break"
 
    def _seleccionar(self):
        seleccion = self.lista.curselection()

        if not seleccion or not self.resultados:
            return

        item = self.resultados[seleccion[0]]
        valor = str(item.get(self.campo_valor, "")).strip()

        self._set_valor_sin_trace(valor)
        self._ocultar_lista()
        self._marcar_seleccionado(True)

        self.entry.focus_set()
        self.entry.icursor(tk.END)

        if self.on_select:
            self.on_select(item)
 # ── selector coincidencia ────────────────────────────────────────────────────           
    def _seleccionar_coincidencia_exacta(self) -> bool:
        texto = self.var_buscar.get().strip()

        if not texto:
            return False

        texto_norm = self._normalizar(texto)

        for item in self.datos:
            valores = [
                item.get(self.campo_valor, ""),
                item.get(self.campo_busqueda, ""),
                *[item.get(c, "") for c in self.campos_extra_busqueda],
            ]

            for valor in valores:
                if self._normalizar(valor) == texto_norm:
                    valor_final = str(item.get(self.campo_valor, "")).strip()

                    self._set_valor_sin_trace(valor_final)
                    self._ocultar_lista()
                    self._marcar_seleccionado(True)

                    self.entry.focus_set()
                    self.entry.icursor(tk.END)

                    if self.on_select:
                        self.on_select(item)

                    return True

        return False
    # ── Validación al salir ────────────────────────────────────────────────────
    def _validar_al_salir(self):
        """Si el usuario escribió sin seleccionar, intenta coincidencia exacta antes de limpiar."""
        focus = self.winfo_toplevel().focus_get()

        if focus in (self.entry, self.lista):
            return

        if not self.var_buscar.get().strip():
            return

        if self._seleccionado:
            return

        if self._seleccionar_coincidencia_exacta():
            return

        if self.permitir_manual:
            self.variable.set(self.var_buscar.get().strip())
            self._ocultar_lista()
            return

        self.var_buscar.set("")
        self.variable.set("")
        self._ocultar_lista()

        if self.on_clear:
            self.on_clear()
    
    # ── Visibilidad de la lista ────────────────────────────────────────────────
    def _ocultar_lista(self):
        self.lista.pack_forget()
 
    # ── API pública ────────────────────────────────────────────────────────────
    def set_valor_externo(self, valor: str, item: dict = None) -> None:
        """Establece un valor programáticamente sin disparar la validación."""
        self._set_valor_sin_trace(valor)
        self._marcar_seleccionado(True)
        self.entry.icursor(tk.END)

        if item and self.on_select:
            self.on_select(item)


    def invalidar_seleccion(self) -> None:
        self._marcar_seleccionado(False)


    def es_seleccion_valida(self) -> bool:
        return self._seleccionado