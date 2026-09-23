
import json

import pytest

from modelos import Cliente
from sistema import SistemaInvernadero


def test_recuperar_si_json_esta_danado_antes_de_iniciar(tmp_path):
    archivo = tmp_path / "datos_invernadero.json"

    # Preparar datos válidos y una copia, sin tocar archivos reales.
    sistema = SistemaInvernadero(archivo_datos=archivo)
    sistema.clientes.append(
        Cliente("Cliente de prueba", "04141234567")
    )
    sistema.guardar_datos()

    copia = sistema.crear_copia_seguridad()
    contenido_valido = copia.read_bytes()

    # Simular que el archivo se dañó antes de abrir el programa.
    archivo.write_text("{json dañado", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        SistemaInvernadero(archivo_datos=archivo)

    # Preparar la recuperación sin cargar el archivo dañado.
    recuperador = SistemaInvernadero(
        archivo_datos=archivo,
        cargar=False
    )

    respaldo_danado = recuperador.restaurar_copia_seguridad(copia)

    assert archivo.read_bytes() == contenido_valido
    assert respaldo_danado is not None
    assert respaldo_danado.read_text(
        encoding="utf-8"
    ) == "{json dañado"

    # Comprobar que un inicio normal vuelve a funcionar.
    sistema_recuperado = SistemaInvernadero(
        archivo_datos=archivo
    )

    assert len(sistema_recuperado.clientes) == 1
    assert sistema_recuperado.clientes[0].nombre == "Cliente de prueba"


@pytest.mark.parametrize(
    "contenido",
    [
        "{}",
        "[]",
        '{"clientes": {}}'
    ]
)
def test_inicio_rechaza_estructura_invalida(tmp_path, contenido):
    archivo = tmp_path / "datos_invernadero.json"
    archivo.write_text(contenido, encoding="utf-8")

    with pytest.raises(ValueError):
        SistemaInvernadero(archivo_datos=archivo)

    # Detectar el error nunca debe sobrescribir los datos.
    assert archivo.read_text(encoding="utf-8") == contenido