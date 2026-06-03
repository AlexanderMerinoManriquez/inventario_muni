import socket
import psutil


def obtener_ip() -> str:
    """
    Retorna la IP de red real del equipo (excluye loopback y direcciones APIPA).

    Estrategia:
    1. Itera las interfaces de red con psutil buscando una IPv4 válida.
       Prioriza interfaces con nombre típico de red cableada/WiFi (Ethernet, Wi-Fi,
       Local Area Connection, etc.) sobre interfaces virtuales o VPN.
    2. Si psutil no encuentra nada útil, cae al método original con socket.
    3. Si todo falla, retorna "IP desconocida".
    """
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        PREFERIDAS = ("ethernet", "wi-fi", "wifi", "local area", "wlan", "eth", "en0", "en1")
        
        DESCARTADAS = ("loopback", "vmware", "virtualbox", "vethernet", "docker",
                       "hyper-v", "pseudo", "teredo", "isatap", "tunnel")

        candidatos_preferidos = []
        candidatos_resto = []

        for nombre_iface, direcciones in interfaces.items():
            nombre_lower = nombre_iface.lower()

            if any(d in nombre_lower for d in DESCARTADAS):
                continue

            iface_stats = stats.get(nombre_iface)
            if iface_stats and not iface_stats.isup:
                continue

            for addr in direcciones:
                if addr.family != socket.AF_INET:
                    continue

                ip = addr.address

                if ip.startswith("127.") or ip.startswith("169.254."):
                    continue

                if any(p in nombre_lower for p in PREFERIDAS):
                    candidatos_preferidos.append(ip)
                else:
                    candidatos_resto.append(ip)

        if candidatos_preferidos:
            return candidatos_preferidos[0]

        if candidatos_resto:
            return candidatos_resto[0]

    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        if not ip.startswith("127."):
            return ip

    except Exception:
        pass

    return "IP desconocida"