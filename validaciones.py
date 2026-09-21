
from datetime import datetime


def validar_fecha_opcional(fecha):
    fecha = fecha.strip()

    if not fecha:
        return ""

    return datetime.strptime(
        fecha, "%d/%m/%Y"
    ).strftime("%d/%m/%Y")