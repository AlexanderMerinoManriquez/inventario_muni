import socket


def obtener_ip() -> str:
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip

    except Exception:
        return "IP desconocida"