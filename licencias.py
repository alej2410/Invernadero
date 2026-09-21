import uuid
import hashlib
import hmac


# ========================================== 
# 0. LICENCIAS POR CLIENTE
# ==========================================
# SECRET_KEY es tuyo y de nadie más. Es lo que te permite generar claves
# válidas para cada invernadero. NUNCA lo subas a un repo público, ni lo
# compartas, ni lo cambies sin razón (si lo cambias, todas las claves que
# ya diste dejan de funcionar).
SECRET_KEY = b"DANIEL-PRIMER_PROGRAMA-LICENCIA-INVERNADERO-2026"


def obtener_id_maquina():
    """Identificador corto y estable de esta computadora (no es 100% infalible,
    pero alcanza para este caso: cambia solo si cambia la tarjeta de red)."""
    mac = str(uuid.getnode())
    return hashlib.sha256(mac.encode()).hexdigest()[:12].upper()


def generar_clave_licencia(id_maquina, nombre_cliente, secreto=SECRET_KEY):
    """Esto lo corres TÚ en tu propia PC (ver generador_licencias.py), nunca
    dentro del programa que le entregas a un cliente."""
    mensaje = f"{id_maquina.strip().upper()}:{nombre_cliente.strip().lower()}".encode()
    firma = hmac.new(secreto, mensaje, hashlib.sha256).hexdigest()[:16].upper()
    return firma


def verificar_clave_licencia(id_maquina, nombre_cliente, clave_ingresada, secreto=SECRET_KEY):
    esperada = generar_clave_licencia(id_maquina, nombre_cliente, secreto)
    return hmac.compare_digest(esperada, clave_ingresada.strip().upper())
