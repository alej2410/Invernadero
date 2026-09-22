
import json

import pytest

from modelos import Cliente
from sistema import SistemaInvernadero


def test_crear_copia_conserva_datos_originales(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()
    cliente = Cliente("José Pérez", "04141234567")

    sistema.clientes.append(cliente)
    sistema.guardar_datos()

    archivo_original = tmp_path / "datos_invernadero.json"
    contenido_original = archivo_original.read_bytes()

    copia = sistema.crear_copia_seguridad()

    assert copia.exists()
    assert copia.parent == tmp_path / "copias_seguridad"
    assert copia.read_bytes() == contenido_original

    # Simular un cambio posterior en los datos del negocio.
    cliente.nombre = "José Pérez García"
    sistema.guardar_datos()

    # El respaldo debe conservar la versión anterior.
    assert copia.read_bytes() == contenido_original
    assert archivo_original.read_bytes() != contenido_original


def test_no_crea_copia_de_json_invalido(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    archivo = tmp_path / "datos_invernadero.json"
    archivo.write_text("{json roto", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        sistema.crear_copia_seguridad()

    assert not (tmp_path / "copias_seguridad").exists()


def test_no_crea_copia_si_falta_archivo(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    with pytest.raises(FileNotFoundError):
        sistema.crear_copia_seguridad()

    assert not (tmp_path / "copias_seguridad").exists()