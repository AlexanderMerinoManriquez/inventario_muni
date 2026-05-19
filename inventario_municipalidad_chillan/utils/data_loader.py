import csv
import json

from utils.rut import formatear_rut

def cargar_funcionarios(path="data/funcionarios.csv"):
    personas = []

    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                personas.append({
                    "rut": formatear_rut(row.get("rut", "")) or "",
                    "nombre": row.get("nombre", "").strip(),
                    "departamento": row.get("departamento", "").strip(),
                })

    except Exception:
        pass

    return personas


def cargar_usuarios_sistema(path="data/usuarios_sistema.csv"):
    personas = []

    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                personas.append({
                    "rut": formatear_rut(row.get("rut", "")) or "",
                    "nombre": row.get("nombre", "").strip(),
                })

    except Exception:
        pass

    return personas

def cargar_departamentos(path="data/departamentos.json"):
    departamentos = []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

            for item in data:
                nombre = str(item.get("nombre", "")).strip()

                if nombre:
                    departamentos.append({
                        "nombre": nombre
                    })

    except Exception:
        pass

    return departamentos