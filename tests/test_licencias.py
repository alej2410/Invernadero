from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licencias import verificar_clave_licencia


def test_verificar_licencia_firmada():
    # Crear claves solamente para esta prueba.
    clave_privada = Ed25519PrivateKey.generate()
    clave_publica_pem = clave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    id_maquina = "ABC123"
    nombre_cliente = "Mi Invernadero"

    # La clave privada firma los datos de esta instalación.
    mensaje = f"{id_maquina}:{nombre_cliente.lower()}".encode("utf-8")
    firma = clave_privada.sign(mensaje).hex()

    # Una licencia auténtica debe aceptarse.
    assert verificar_clave_licencia(
        id_maquina,
        nombre_cliente,
        firma,
        clave_publica_pem=clave_publica_pem
    )

    # La misma licencia no debe funcionar para otro invernadero.
    assert not verificar_clave_licencia(
        id_maquina,
        "Otro Invernadero",
        firma,
        clave_publica_pem=clave_publica_pem
    )

    # Una licencia auténtica tampoco debe funcionar en otro equipo.
    assert not verificar_clave_licencia(
        "OTRA-PC",
        nombre_cliente,
        firma,
        clave_publica_pem=clave_publica_pem
    )

    # Una firma alterada debe rechazarse.
    firma_alterada = ("00" if firma[:2] != "00" else "01") + firma[2:]

    assert not verificar_clave_licencia(
        id_maquina,
        nombre_cliente,
        firma_alterada,
        clave_publica_pem=clave_publica_pem
    )