def clasificar_tipo_disco(modelo, tipo):

    modelo_lower = modelo.lower()
    tipo_lower = tipo.lower()

    # NVMe siempre es SSD
    if "nvme" in tipo_lower:
        return "SSD"

    # Si el modelo dice SSD
    if "ssd" in modelo_lower:
        return "SSD"

    # ATA puede ser HDD o SSD
    # si no dice SSD en el modelo asumimos HDD
    if "ata" in tipo_lower:
        if "ssd" in modelo_lower:
            return "SSD"
        return "HDD"

    return "HDD"
