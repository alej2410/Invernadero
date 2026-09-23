from rutas import obtener_ruta_datos
from modelos import Cliente
from sistema import SistemaInvernadero

def test_ruta_datos_usa_carpeta_local(tmp_path, monkeypatch):
    carpeta_local = tmp_path / "AppData" / "Local"
    monkeypatch.setenv("LOCALAPPDATA", str(carpeta_local))

    ruta = obtener_ruta_datos()

    assert ruta == (
        carpeta_local / "Invernadero" / "datos_invernadero.json"
    )


def test_ruta_no_depende_de_carpeta_de_ejecucion(
    tmp_path, monkeypatch
):
    carpeta_local = tmp_path / "AppData" / "Local"
    monkeypatch.setenv("LOCALAPPDATA", str(carpeta_local))

    ruta_original = obtener_ruta_datos()

    otra_carpeta = tmp_path / "otra_carpeta"
    otra_carpeta.mkdir()
    monkeypatch.chdir(otra_carpeta)

    assert obtener_ruta_datos() == ruta_original
    assert not ruta_original.exists()

def test_guardar_crea_carpeta_de_datos(tmp_path):
    archivo = (
        tmp_path
        / "carpeta_que_no_existe"
        / "datos_invernadero.json"
    )

    sistema = SistemaInvernadero(archivo_datos=archivo)
    sistema.clientes.append(
        Cliente("Cliente de prueba", "04141234567")
    )

    sistema.guardar_datos()

    assert archivo.is_file()

    recuperado = SistemaInvernadero(archivo_datos=archivo)
    assert recuperado.clientes[0].nombre == "Cliente de prueba"