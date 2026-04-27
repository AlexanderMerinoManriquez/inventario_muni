import wmi

def obtener_info_discos():
    c = wmi.WMI()
    return c.Win32_DiskDrive()