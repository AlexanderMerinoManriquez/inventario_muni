def calcular_salud(horas, errores, temperatura):

    salud = 100

    if errores is None:
        errores = 0

    if horas is None:
        horas = 0

    if temperatura is None:
        temperatura = 0

    if errores > 0:
        salud -= min(errores * 5, 50)

    if horas > 30000:
        salud -= 20
    elif horas > 20000:
        salud -= 10
    elif horas > 10000:
        salud -= 5

    if temperatura > 60:
        salud -= 15
    elif temperatura > 50:
        salud -= 5

    return max(0, salud)
