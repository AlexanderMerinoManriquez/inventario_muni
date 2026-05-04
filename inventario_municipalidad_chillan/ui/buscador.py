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
        self.resultados = []
        self._seleccionado = False   # True sólo tras elegir un ítem de la lista
 
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
 
        # Indicador visual: muestra ✓ verde cuando hay selección válida
        self._lbl_estado = tk.Label(
            barra,
            text="",
            bg=C["gris_panel"],
            font=("Segoe UI", 10, "bold"),
            width=2,
        )
        self._lbl_estado.pack(side="left", padx=(4, 0))
 
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
        self.var_buscar.trace_add("write", lambda *_: self._on_escribir())
        self.lista.bind("<ButtonRelease-1>", lambda e: self._seleccionar())
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
        return texto.translate(tabla).replace("-", " ").lower()
 
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
        if ok:
            self._lbl_estado.config(text="✓", fg=C.get("verde", "#4caf50"))
        else:
            self._lbl_estado.config(text="")
 
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
            return "break"
        size = self.lista.size()
        actual = self.lista.curselection()
        idx = (actual[0] + delta) if actual else (0 if delta > 0 else size - 1)
        idx = max(0, min(idx, size - 1))
        self.lista.selection_clear(0, tk.END)
        self.lista.selection_set(idx)
        self.lista.see(idx)
        self.lista.focus_set()
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
 
        # Desconectar trace temporalmente para evitar que _on_escribir
        # marque como no-seleccionado al hacer .set()
        self.var_buscar.trace_remove("write", self.var_buscar.trace_info()[0][1])
        self.var_buscar.set(valor)
        self.var_buscar.trace_add("write", lambda *_: self._on_escribir())
 
        self.variable.set(valor)
        self._ocultar_lista()
        self._marcar_seleccionado(True)
        self.entry.focus_set()
 
        if self.on_select:
            self.on_select(item)
 
    # ── Validación al salir ────────────────────────────────────────────────────
    def _validar_al_salir(self):
        """Si el usuario escribió sin seleccionar, limpia el campo."""
        focus = self.winfo_toplevel().focus_get()
        if focus in (self.entry, self.lista):
            return  # El foco sigue en el buscador
 
        if self.var_buscar.get().strip() and not self._seleccionado:
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
        """Establece un valor programáticamente (sin disparar validación)."""
        self.var_buscar.trace_remove("write", self.var_buscar.trace_info()[0][1])
        self.var_buscar.set(valor)
        self.var_buscar.trace_add("write", lambda *_: self._on_escribir())
        self.variable.set(valor)
        self._marcar_seleccionado(True)
        if item and self.on_select:
            self.on_select(item)