import tkinter as tk

from tkinter import ttk
from config import C

class BuscadorDepartamento(tk.Frame):
    MIN_CHARS = 2
    MAX_RESULTADOS = 8

    def __init__(self, parent, opciones, variable, on_select=None,  **kwargs):
        super().__init__(parent, bg=C["gris_panel"])

        self.opciones = sorted(opciones)
        self.variable = variable
        self.on_select = on_select

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

    def _normalizar(self, texto: str) -> str:
        tabla = str.maketrans("áéíóúÁÉÍÓÚüÜñÑ", "aeiouAEIOUuUnN")
        return texto.translate(tabla).replace("-", " ").lower()

    def _filtrar(self):
        texto = self._normalizar(self.var_buscar.get().strip())

        if not texto:
            self.variable.set("")
            if self.on_select:
                self.on_select("")
            self._ocultar_lista()
            return

        if len(texto) < self.MIN_CHARS:
            self._ocultar_lista()
            return

        palabras = texto.split()

        coinciden = [
            dep for dep in self.opciones
            if all(p in self._normalizar(dep) for p in palabras)
        ]

        empiezan = [
            dep for dep in coinciden
            if self._normalizar(dep).startswith(texto)
        ]
        resto = [dep for dep in coinciden if dep not in empiezan]
        resultados = (empiezan + resto)[:self.MAX_RESULTADOS]

        self.lista.delete(0, tk.END)

        if not resultados:
            self._ocultar_lista()
            return

        for dep in resultados:
            self.lista.insert(tk.END, dep)

        self.lista.config(height=len(resultados))
        self.lista.pack(fill="x", pady=(3, 0))

    def _seleccionar_primero(self):
        if self.lista.size() > 0:
            self.lista.selection_clear(0, tk.END)
            self.lista.selection_set(0)
            self._seleccionar()
            return "break"

    def _seleccionar(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return

        valor = self.lista.get(seleccion[0])
        self.var_buscar.set(valor)
        self.variable.set(valor)
        self._ocultar_lista()

        if self.on_select:
            self.on_select(valor)

    def _ocultar_lista(self):
        self.lista.pack_forget()