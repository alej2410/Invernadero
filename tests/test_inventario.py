
from modelos import Cliente, Pedido, PartePedido
from sistema import SistemaInvernadero


def test_inventario_distingue_clientes_mismo_nombre(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    cliente1 = Cliente("José Pérez", "04141111111")
    cliente2 = Cliente("José Pérez", "04242222222")

    pedido1 = Pedido(cliente1)
    pedido2 = Pedido(cliente2)

    pedido1.agregar_parte(
        PartePedido("Tomate", 10, 5.0, "20/09/2026", "A1")
    )

    pedido2.agregar_parte(
        PartePedido("Tomate", 20, 5.0, "20/09/2026", "A2")
    )

    cliente1.pedidos.append(pedido1)
    cliente2.pedidos.append(pedido2)

    sistema.clientes.extend([cliente1, cliente2])

    inventario = sistema.reporte_inventario_activo()

    tomate = inventario["tomate"]

    assert tomate["total"] == 30

    # Cada cliente debe tener su propia entrada.
    assert len(tomate["clientes"]) == 2

    assert tomate["clientes"][cliente1.id]["cantidad"] == 10
    assert tomate["clientes"][cliente2.id]["cantidad"] == 20

    assert (
        tomate["clientes"][cliente1.id]["telefono"]
        == "04141111111"
    )

    assert (
        tomate["clientes"][cliente2.id]["telefono"]
        == "04242222222"
    )