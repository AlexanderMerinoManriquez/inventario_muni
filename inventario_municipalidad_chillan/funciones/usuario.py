def pedir_nombre_completo():
    print("Por favor ingresa tu información:")

    nombre = input("Nombre: ").strip().lower()
    while not nombre:
        print("El nombre no puede estar vacío.")
        nombre = input("Nombre: ").strip().lower()

    apellido1 = input("Primer Apellido: ").strip().lower()
    while not apellido1:
        print("El primer apellido no puede estar vacío.")
        apellido1 = input("Primer Apellido: ").strip().lower()

    apellido2 = input("Segundo Apellido: ").strip().lower()
    while not apellido2:
        print("El segundo apellido no puede estar vacío.")
        apellido2 = input("Segundo Apellido: ").strip().lower()

    return {
        "nombre": nombre,
        "apellido1": apellido1,
        "apellido2": apellido2
    }