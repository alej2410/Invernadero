
from sistema import SistemaInvernadero
from modelos import Cliente, Pedido, PartePedido


def test_guardar_y_cargar_datos(tmp_path, monkeypatch):
    # Utilizar una carpeta temporal para no tocar los datos reales
    monkeypatch.chdir(tmp_path)

    # Crear un sistema vacío
    sistema = SistemaInvernadero()

    # Registrar un cliente
    cliente = Cliente("Juan Pérez", "04141234567")

    # Crear un pedido
    pedido = Pedido(cliente)

    parte = PartePedido(
        especie="Tomate",
        cantidad=10,
        precio=5.0,
        fecha_siembra="20/09/2026",
        ubicacion="A1"
    )

    pedido.agregar_parte(parte)
    pedido.registrar_abono(20.0)

    cliente.pedidos.append(pedido)
    sistema.clientes.append(cliente)

    # Guardar la información en JSON
    sistema.guardar_datos()

    # Simular el cierre y la reapertura del programa
    sistema_recuperado = SistemaInvernadero()

    # Verificar los datos recuperados
    assert len(sistema_recuperado.clientes) == 1

    cliente_recuperado = sistema_recuperado.clientes[0]

    assert cliente_recuperado.nombre == "Juan Pérez"
    assert cliente_recuperado.telefono == "04141234567"
    assert len(cliente_recuperado.pedidos) == 1

    pedido_recuperado = cliente_recuperado.pedidos[0]

    assert pedido_recuperado.calcular_total() == 50.0
    assert pedido_recuperado.total_abonado() == 20.0
    assert pedido_recuperado.saldo_pendiente() == 30.0

    assert pedido_recuperado.partes[0].especie == "Tomate"
    assert pedido_recuperado.partes[0].ubicacion == "A1"