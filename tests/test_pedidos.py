
from app_grafica import Cliente, Pedido, PartePedido


def crear_pedido_de_prueba():
    cliente = Cliente("Juan Pérez", "04141234567")
    pedido = Pedido(cliente)

    parte = PartePedido(
        especie="Tomate",
        cantidad=10,
        precio=5.0,
        fecha_siembra="20/09/2026",
        ubicacion="A1"
    )

    pedido.agregar_parte(parte)
    return pedido


def test_total_pedido():
    pedido = crear_pedido_de_prueba()
    assert pedido.calcular_total() == 50.0


def test_saldo_inicial():
    pedido = crear_pedido_de_prueba()
    assert pedido.saldo_pendiente() == 50.0


def test_abono_parcial():
    pedido = crear_pedido_de_prueba()
    pedido.registrar_abono(20.0)

    assert pedido.total_abonado() == 20.0
    assert pedido.saldo_pendiente() == 30.0


def test_pago_completo():
    pedido = crear_pedido_de_prueba()
    pedido.registrar_abono(50.0)

    assert pedido.saldo_pendiente() == 0.0
  