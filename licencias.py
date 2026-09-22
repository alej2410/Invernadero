
import hashlib
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)


# Más adelante colocaremos aquí TU clave pública.
# Nunca colocaremos una clave privada en este archivo.
CLAVE_PUBLICA_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAuM3LVVxUZr/S+IX7DsA4Rm37RhdC2ad1jgFIaLkrXR4=
-----END PUBLIC KEY-----
"""


def obtener_id_maquina():
    mac = str(uuid.getnode())
    return hashlib.sha256(mac.encode()).hexdigest()[:12].upper()


def verificar_clave_licencia(
    id_maquina,
    nombre_cliente,
    clave_ingresada,
    clave_publica_pem=None,
):
    # En las pruebas se puede proporcionar una clave pública temporal.
    # En la aplicación se utilizará la clave pública configurada arriba.
    pem = (
        clave_publica_pem
        if clave_publica_pem is not None
        else CLAVE_PUBLICA_PEM
    )

    # Sin clave pública configurada, no aceptar ninguna licencia.
    if pem is None:
        return False

    mensaje = (
        f"{id_maquina.strip().upper()}:"
        f"{nombre_cliente.strip().lower()}"
    ).encode("utf-8")

    try:
        clave_publica = serialization.load_pem_public_key(pem)

        if not isinstance(clave_publica, Ed25519PublicKey):
            return False

        # La licencia se representa como texto hexadecimal.
        firma = bytes.fromhex(clave_ingresada.strip())

        # Si la firma o el mensaje no coinciden, verify() lanza
        # InvalidSignature.
        clave_publica.verify(firma, mensaje)

        return True

    except (InvalidSignature, ValueError, TypeError):
        return False