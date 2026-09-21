
from modelos import Cliente, Pedido, PartePedido
from sistema import SistemaInvernadero


def test_clientes_mismo_nombre_mantienen_sus_pedidos(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    sistema = SistemaInvernadero()

    # Dos personas distintas con el mismo nombre.
    cliente1 = Cliente("José Pérez", "04141111111")
    cliente2 = Cliente("José Pérez", "04242222222")

    # Cada persona tiene su propio pedido.
    pedido1 = Pedido(cliente1)
    pedido2 = Pedido(cliente2)

    pedido1.agregar_parte(
        PartePedido("Tomate", 10, 5.0, "20/09/2026", "A1")
    )

    pedido2.agregar_parte(
        PartePedido("Lechuga", 20, 3.0, "20/09/2026", "B1")
    )

    cliente1.pedidos.append(pedido1)
    cliente2.pedidos.append(pedido2)

    sistema.clientes.extend([cliente1, cliente2])

    sistema.guardar_datos()

    # Simulamos cerrar y volver a abrir.
    sistema_recuperado = SistemaInvernadero()

    assert len(sistema_recuperado.clientes) == 2

    # Identificamos a cada persona por su UUID.
    clientes = {
        cliente.id: cliente
        for cliente in sistema_recuperado.clientes
    }

    recuperado1 = clientes[cliente1.id]
    recuperado2 = clientes[cliente2.id]

    assert recuperado1.nombre == "José Pérez"
    assert recuperado2.nombre == "José Pérez"

    assert recuperado1.pedidos[0].calcular_total() == 50.0
    assert recuperado2.pedidos[0].calcular_total() == 60.0

    # Modificamos solamente al primer cliente.
    recuperado1.nombre = "José Pérez García"
    recuperado1.telefono = "04149999999"

    sistema_recuperado.guardar_datos()

    # Volvemos a cargar para comprobar la persistencia.
    sistema_final = SistemaInvernadero()

    clientes_finales = {
        cliente.id: cliente
        for cliente in sistema_final.clientes
    }

    assert (
        clientes_finales[cliente1.id].nombre
        == "José Pérez García"
    )

    assert (
        clientes_finales[cliente1.id].telefono
        == "04149999999"
    )

    # El segundo cliente permanece intacto.
    assert clientes_finales[cliente2.id].nombre == "José Pérez"

    assert (
        clientes_finales[cliente2.id].telefono
        == "04242222222"
    )

    assert (
        clientes_finales[cliente2.id]
        .pedidos[0].calcular_total()
        == 60.0
    )