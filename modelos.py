from datetime import datetime

class Cliente: 
    def __init__(self, nombre, telefono, cedula="", direccion=""): 
        self.nombre = nombre 
        self.telefono = telefono 
        self.cedula = cedula
        self.direccion = direccion
        self.pedidos = [] 

    def to_dict(self): 
        return { 
            'nombre': self.nombre, 
            'telefono': self.telefono, 
            'cedula': self.cedula,
            'direccion': self.direccion,
            'pedidos': [pedido.to_dict() for pedido in self.pedidos] 
        } 

    def __str__(self): 
        return f"Cliente: {self.nombre}, Teléfono: {self.telefono}" 

    def saldo_pendiente(self): 
        return sum(pedido.saldo_pendiente() for pedido in self.pedidos) 


class PartePedido: 
    def __init__(self, especie, cantidad, precio, fecha_siembra, ubicacion, entregado=False, fecha_estimada=""): 
        self.especie = especie 
        self.cantidad = cantidad 
        self.precio = precio 
        self.fecha_siembra = fecha_siembra 
        self.ubicacion = ubicacion 
        self.entregado = entregado 
        self.fecha_estimada = fecha_estimada

    def calcular_total(self): 
        return self.cantidad * self.precio 

    def to_dict(self): 
        return { 
            'especie': self.especie, 
            'cantidad': self.cantidad, 
            'precio': self.precio, 
            'fecha_siembra': self.fecha_siembra, 
            'ubicacion': self.ubicacion, 
            'entregado': self.entregado,
            'fecha_estimada': self.fecha_estimada
        } 


class Pedido: 
    def __init__(self, cliente): 
        self.cliente = cliente 
        self.partes = [] 
        self.abonos = [] 
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S") 

    def agregar_parte(self, parte): 
        self.partes.append(parte) 

    def calcular_total(self): 
        total = 0 
        for parte in self.partes: 
            total += parte.calcular_total() 
        return total 

    def registrar_abono(self, monto, fecha=None): 
        if not fecha: 
            fecha = datetime.now().strftime("%d/%m/%Y") 
        self.abonos.append({'monto': monto, 'fecha': fecha}) 

    def total_abonado(self): 
        total = 0 
        for abono in self.abonos: 
            total += abono['monto'] 
        return total 

    def saldo_pendiente(self): 
        return self.calcular_total() - self.total_abonado() 

    def to_dict(self): 
        return { 
            'fecha': self.fecha, 
            'partes': [parte.to_dict() for parte in self.partes], 
            'abonos': self.abonos 
        } 
