import os
from pathlib import Path


def obtener_ruta_datos():
    carpeta_local = os.environ.get("LOCALAPPDATA")

    if carpeta_local:
        base = Path(carpeta_local)
    else:
        base = Path.home() / "AppData" / "Local"

    return base / "Invernadero" / "datos_invernadero.json"