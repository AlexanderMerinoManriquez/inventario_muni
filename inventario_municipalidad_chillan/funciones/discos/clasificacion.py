def clasificar_tipo_disco(modelo, tipo):
    texto = f"{modelo or ''} {tipo or ''}".lower()

    claves_ssd = (
        "ssd",
        "nvme",
        "m.2",
        "pcie",
        "solid state",
        "kingston",
        "crucial",
        "wd green",
        "wd blue sn",
        "samsung mz",
        "sandisk",
        "adata",
        "lexar",
    )

    if any(clave in texto for clave in claves_ssd):
        return "SSD"

    claves_hdd = (
        "hdd",
        "hard disk",
        "st",          
        "wd10",
        "wd500",
        "wd320",
        "toshiba mq",
        "hitachi",
        "travelstar",
    )

    if any(clave in texto for clave in claves_hdd):
        return "HDD"

    return "Disco"