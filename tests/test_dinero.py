
from decimal import Decimal

from modelos import Cliente, Pedido, PartePedido
from sistema import SistemaInvernadero


def test_importes_decimales_se_conservan_al_guardar(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    cliente = Cliente("Pedro", "04141234567")
    pedido = Pedido(cliente)

    parte = PartePedido(
        especie="Tomate",
        cantidad=3,
        precio=Decimal("0.10"),
        fecha_siembra="21/09/2026",
        ubicacion="A1"
    )

    pedido.agregar_parte(parte)
    pedido.registrar_abono(Decimal("0.10"))

    cliente.pedidos.append(pedido)
    sistema.clientes.append(cliente)

    # Guardar los datos.
    sistema.guardar_datos()

    # Simular que cerramos y abrimos el programa.
    sistema_recuperado = SistemaInvernadero()

    pedido_recuperado = (
        sistema_recuperado.clientes[0].pedidos[0]
    )

    # Comprobar que los importes siguen siendo Decimal.
    assert (
        pedido_recuperado.partes[0].precio
        == Decimal("0.10")
    )

    assert isinstance(
        pedido_recuperado.partes[0].precio,
        Decimal
    )

    assert (
        pedido_recuperado.total_abonado()
        == Decimal("0.10")
    )

    assert pedido_recuperado.calcular_total() == Decimal("0.30")
    assert pedido_recuperado.saldo_pendiente() == Decimal("0.20")