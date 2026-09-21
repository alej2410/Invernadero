
import json

import pytest

from modelos import Cliente
from sistema import SistemaInvernadero


def test_error_al_guardar_no_destruye_datos(
    tmp_path, monkeypatch
):
    # Trabajar únicamente con archivos temporales.
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    cliente = Cliente("José Pérez", "04141234567")
    sistema.clientes.append(cliente)

    # Guardar una versión válida.
    sistema.guardar_datos()

    archivo = tmp_path / "datos_invernadero.json"
    contenido_original = archivo.read_bytes()

    # Modificar la información en memoria.
    cliente.nombre = "José Pérez García"

    # Simular un error durante la escritura del JSON.
    def escritura_fallida(*args, **kwargs):
        raise OSError("Error simulado durante el guardado")

    monkeypatch.setattr(json, "dump", escritura_fallida)

    with pytest.raises(OSError):
        sistema.guardar_datos()

    # El archivo original debe conservarse intacto.
    assert archivo.read_bytes() == contenido_original