
import json

import pytest

from modelos import Cliente
from sistema import SistemaInvernadero


def test_restaurar_recupera_datos_y_conserva_version_anterior(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()
    cliente = Cliente("José Pérez", "04141234567")
    sistema.clientes.append(cliente)
    sistema.guardar_datos()

    copia = sistema.crear_copia_seguridad()
    contenido_de_la_copia = copia.read_bytes()

    # Guardar cambios posteriores.
    cliente.nombre = "José Pérez García"
    sistema.guardar_datos()

    archivo = tmp_path / "datos_invernadero.json"
    contenido_anterior = archivo.read_bytes()

    # Volver a la versión de la copia.
    respaldo_anterior = sistema.restaurar_copia_seguridad(copia)

    assert archivo.read_bytes() == contenido_de_la_copia
    assert sistema.clientes[0].nombre == "José Pérez"

    # La versión que reemplazamos también quedó guardada.
    assert respaldo_anterior is not None
    assert respaldo_anterior.read_bytes() == contenido_anterior


def test_copia_invalida_no_reemplaza_datos(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()
    sistema.clientes.append(
        Cliente("José Pérez", "04141234567")
    )
    sistema.guardar_datos()

    archivo = tmp_path / "datos_invernadero.json"
    contenido_original = archivo.read_bytes()

    copia_invalida = tmp_path / "copia_invalida.json"
    copia_invalida.write_text(
        '{"clientes": "esto no es una lista"}',
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        sistema.restaurar_copia_seguridad(copia_invalida)

    assert archivo.read_bytes() == contenido_original
    assert sistema.clientes[0].nombre == "José Pérez"


def test_restaurar_conserva_archivo_actual_corrupto(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()
    sistema.clientes.append(
        Cliente("José Pérez", "04141234567")
    )
    sistema.guardar_datos()

    copia = sistema.crear_copia_seguridad()

    archivo = tmp_path / "datos_invernadero.json"
    archivo.write_text("{archivo dañado", encoding="utf-8")

    respaldo_anterior = sistema.restaurar_copia_seguridad(copia)

    # Recuperamos el JSON válido.
    datos = json.loads(archivo.read_text(encoding="utf-8"))
    assert len(datos["clientes"]) == 1

    # No destruimos el archivo dañado que sustituimos.
    assert respaldo_anterior is not None
    assert respaldo_anterior.read_text(
        encoding="utf-8"
    ) == "{archivo dañado"


def test_copia_inexistente_no_modifica_datos(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()
    sistema.guardar_datos()

    archivo = tmp_path / "datos_invernadero.json"
    contenido_original = archivo.read_bytes()

    with pytest.raises(FileNotFoundError):
        sistema.restaurar_copia_seguridad(
            tmp_path / "no_existe.json"
        )

    assert archivo.read_bytes() == contenido_original