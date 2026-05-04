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
        formato_resultado=None,
        on_select=None,
        **kwargs
    ):
        super().__init__(parent, bg=C["gris_panel"])

        self.datos = datos or []
        self.variable = variable
        self.campo_busqueda = campo_busqueda
        self.formato_resultado = formato_resultado or self._formato_default
        self.on_select = on_select
        self.resultados = []

        self.var_buscar = tk.StringVar(value=variable.get())

        barra = ttk.Frame(self)
        barra.pack(fill="x")

        tk.Label(
            barra,
            text="⌕",
            bg=C["gris_panel"],
            fg=C["gris_sub"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=(0, 6))

        self.entry = ttk.Entry(barra, textvariable=self.var_buscar, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)

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

        self.var_buscar.trace_add("write", lambda *_: self._filtrar())
        self.lista.bind("<ButtonRelease-1>", lambda e: self._seleccionar())
        self.lista.bind("<Return>", lambda e: self._seleccionar())
        self.entry.bind("<Return>", lambda e: self._seleccionar_primero())
        self.entry.bind("<Escape>", lambda e: self._ocultar_lista())

    def _formato_default(self, item: dict) -> str:
        nombre = str(item.get(self.campo_busqueda, ""))
        rut = str(item.get("rut", ""))

        return f"{nombre} — {rut}" if rut else nombre

    def _normalizar(self, texto: str) -> str:
        tabla = str.maketrans("áéíóúÁÉÍÓÚüÜñÑ", "aeiouAEIOUuUnN")
        return texto.translate(tabla).replace("-", " ").lower()

    def _filtrar(self):
        texto = self._normalizar(self.var_buscar.get().strip())

        if not texto:
            self.variable.set("")
            self.resultados = []
            self._ocultar_lista()
            return

        if len(texto) < self.MIN_CHARS:
            self._ocultar_lista()
            return

        palabras = texto.split()

        coinciden = [
            item for item in self.datos
            if all(
                palabra in self._normalizar(str(item.get(self.campo_busqueda, "")))
                for palabra in palabras
            )
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
        valor = str(item.get(self.campo_busqueda, ""))

        self.var_buscar.set(valor)
        self.variable.set(valor)
        self._ocultar_lista()

        if self.on_select:
            self.on_select(item)

    def _ocultar_lista(self):
        self.lista.pack_forget()