import json

from modelos import Cliente, Pedido, PartePedido

# ========================================== 
# 1. EL MODELO (TUS CLASES DE DATOS) 
# ========================================== 

class SistemaInvernadero: 
    def __init__(self): 
        self.clientes = [] 
        self.archivo_datos = "datos_invernadero.json" 
        self.cargar_datos() 

    def guardar_datos(self): 
        datos = { 
            'clientes': [cliente.to_dict() for cliente in self.clientes] 
        } 
        with open(self.archivo_datos, 'w', encoding='utf-8') as archivo: 
            json.dump(datos, archivo, ensure_ascii=False, indent=4) 

    def cargar_datos(self): 
        try: 
            with open(self.archivo_datos, 'r', encoding='utf-8') as archivo: 
                datos = json.load(archivo) 
        except FileNotFoundError: 
            self.clientes = [] 
            return 

        clientes_temporales = [] 
        for datos_cliente in datos.get('clientes', []): 
            # Lectura a prueba de fallos para clientes viejos
            cliente = Cliente(
                datos_cliente['nombre'], 
                datos_cliente['telefono'],
                datos_cliente.get('cedula', ''),
                datos_cliente.get('direccion', ''),
                id=datos_cliente['id']
            )
            for datos_pedido in datos_cliente.get('pedidos', []): 
                pedido = Pedido(cliente) 
                pedido.fecha = datos_pedido.get('fecha', pedido.fecha) 
                for datos_parte in datos_pedido.get('partes', []): 
                    parte = PartePedido( 
                        datos_parte['especie'], 
                        datos_parte['cantidad'], 
                        datos_parte['precio'], 
                        datos_parte['fecha_siembra'], 
                        datos_parte['ubicacion'], 
                        datos_parte.get('entregado', False),
                        datos_parte.get('fecha_estimada', '')
                    ) 
                    pedido.agregar_parte(parte) 
                pedido.abonos = datos_pedido.get('abonos', []) 
                cliente.pedidos.append(pedido) 
            clientes_temporales.append(cliente) 
        
        self.clientes = clientes_temporales 

    def encontrar_clientes_parcial(self, busqueda):
        """Busca cualquier coincidencia parcial en el nombre y devuelve una lista"""
        busqueda = busqueda.lower().strip()
        if not busqueda:
            return self.clientes 
        
        resultados = []
        for cliente in self.clientes:
            if busqueda in cliente.nombre.lower():
                resultados.append(cliente)
        return resultados

    def encontrar_cliente(self, nombre): 
        for cliente in self.clientes: 
            if cliente.nombre.lower() == nombre.lower(): 
                return cliente 
        return None 

    def reporte_deudores(self): 
        deudores = [] 
        total_global_deuda = 0 
        for cliente in self.clientes: 
            deuda_cliente = 0 
            resumen_plantas = {} 
            for pedido in cliente.pedidos: 
                deuda_cliente += pedido.saldo_pendiente() 
                for parte in pedido.partes: 
                    if not parte.entregado: 
                        esp = parte.especie.lower().strip() 
                        resumen_plantas[esp] = resumen_plantas.get(esp, 0) + parte.cantidad 
            if deuda_cliente > 0: 
                deudores.append({ 
                    'nombre': cliente.nombre, 
                    'telefono': cliente.telefono, 
                    'deuda': deuda_cliente, 
                    'plantas': resumen_plantas 
                }) 
                total_global_deuda += deuda_cliente 
        deudores.sort(key=lambda x: x['deuda'], reverse=True) 
        return deudores, total_global_deuda 

    
    def reporte_inventario_activo(self):
        inventario = {}

        for cliente in self.clientes:
            for pedido in cliente.pedidos:
                for parte in pedido.partes:

                    if parte.entregado:
                        continue

                    especie = parte.especie.lower().strip()

                    # Crear el grupo de la especie.
                    if especie not in inventario:
                        inventario[especie] = {
                            "total": 0,
                            "clientes": {}
                        }

                    inventario[especie]["total"] += parte.cantidad

                    clientes_especie = inventario[especie]["clientes"]

                    # El UUID identifica al cliente internamente.
                    if cliente.id not in clientes_especie:
                        clientes_especie[cliente.id] = {
                            "nombre": cliente.nombre,
                            "telefono": cliente.telefono,
                            "cantidad": 0
                        }

                    # Acumular las bandejas del cliente correcto.
                    clientes_especie[cliente.id]["cantidad"] += (
                        parte.cantidad
                    )

        return inventario
