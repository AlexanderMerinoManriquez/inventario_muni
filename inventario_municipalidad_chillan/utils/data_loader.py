import csv

def cargar_funcionarios(path="data/funcionarios.csv"):
    personas = []

    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                personas.append({
                    "rut": row.get("rut", "").strip(),
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
                    "rut": row.get("rut", "").strip(),
                    "nombre": row.get("nombre", "").strip(),
                })

    except Exception:
        pass

    return personas