import json
import os
import tempfile
import shutil
from pathlib import Path
from modelos import Cliente, Pedido, PartePedido
from datetime import datetime, timezone
from uuid import uuid4

# ========================================== 
# 1. EL MODELO (TUS CLASES DE DATOS) 
# ========================================== 

class SistemaInvernadero: 
    def __init__(self, archivo_datos="datos_invernadero.json"):
        self.clientes = []
        self.archivo_datos = archivo_datos
        self.cargar_datos() 

    
    def guardar_datos(self):
        datos = {
            "clientes": [
                cliente.to_dict()
                for cliente in self.clientes
            ]
        }

        archivo = Path(self.archivo_datos)
        archivo_temporal = None

        try:
            # Crear un archivo temporal en la misma carpeta.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=archivo.absolute().parent,
                prefix=f".{archivo.name}.",
                suffix=".tmp",
                delete=False
            ) as temporal:

                archivo_temporal = Path(temporal.name)

                # Escribir los nuevos datos.
                json.dump(
                    datos,
                    temporal,
                    ensure_ascii=False,
                    indent=4
                )

                # Vaciar los buffers de Python y solicitar
                # la escritura de los datos al sistema.
                temporal.flush()
                os.fsync(temporal.fileno())

            # Reemplazar el original solamente cuando
            # la escritura haya terminado correctamente.
            os.replace(archivo_temporal, archivo)

        except Exception:
            # Si ocurre un error, eliminar el temporal.
            if archivo_temporal is not None:
                archivo_temporal.unlink(missing_ok=True)

            # Propagar el error para no fingir que guardamos.
            raise 


    def crear_copia_seguridad(self, carpeta_destino=None):
        """Crea una copia independiente del JSON actual."""

        origen = Path(self.archivo_datos).resolve()

        # No crear una copia vacía si aún no hay datos guardados.
        contenido = origen.read_bytes()

        # Comprobar que el archivo contiene un JSON con
        # la estructura básica esperada por el sistema.
        datos = json.loads(contenido.decode("utf-8"))

        if (
            not isinstance(datos, dict)
            or not isinstance(datos.get("clientes"), list)
        ):
            raise ValueError(
                "El archivo de datos no tiene una estructura válida"
            )

        if carpeta_destino is None:
            carpeta = origen.parent / "copias_seguridad"
        else:
            carpeta = Path(carpeta_destino).resolve()

        carpeta.mkdir(parents=True, exist_ok=True)

        fecha = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        identificador = uuid4().hex[:8]

        destino = carpeta / (
            f"datos_invernadero_{fecha}_{identificador}.json"
        )

        archivo_temporal = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=carpeta,
                prefix=".copia_",
                suffix=".tmp",
                delete=False
            ) as temporal:
                archivo_temporal = Path(temporal.name)
                temporal.write(contenido)
                temporal.flush()
                os.fsync(temporal.fileno())

            # Verificar que la copia puede cargarse completamente.
            SistemaInvernadero(archivo_datos=archivo_temporal)

            os.replace(archivo_temporal, destino)
            return destino

        except Exception:
            if archivo_temporal is not None:
                archivo_temporal.unlink(missing_ok=True)
            raise

    def restaurar_copia_seguridad(self, ruta_copia):
        """Restaura una copia y conserva el archivo anterior."""

        copia = Path(ruta_copia).resolve()
        archivo_actual = Path(self.archivo_datos).resolve()

        if copia == archivo_actual:
            raise ValueError(
                "No puedes restaurar el archivo sobre sí mismo"
            )

        # Leer y validar la estructura básica ANTES de tocar
        # los datos actuales.
        contenido = copia.read_bytes()
        datos = json.loads(contenido.decode("utf-8"))

        if (
            not isinstance(datos, dict)
            or not isinstance(datos.get("clientes"), list)
        ):
            raise ValueError(
                "La copia no tiene una estructura válida"
            )

        temporal = None
        respaldo_anterior = None

        try:
            # Preparar la restauración en un archivo temporal.
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=archivo_actual.parent,
                prefix=".restauracion_",
                suffix=".tmp",
                delete=False
            ) as destino_temporal:
                temporal = Path(destino_temporal.name)
                destino_temporal.write(contenido)
                destino_temporal.flush()
                os.fsync(destino_temporal.fileno())

            # Comprobar también que el sistema puede
            # reconstruir clientes y pedidos desde esta copia.
            sistema_validacion = SistemaInvernadero(
                archivo_datos=temporal
            )

            # Conservar el archivo anterior, incluso si su
            # contenido está dañado.
            if archivo_actual.exists():
                carpeta = archivo_actual.parent / "copias_seguridad"
                carpeta.mkdir(parents=True, exist_ok=True)

                identificador = uuid4().hex
                respaldo_anterior = carpeta / (
                    f"antes_restauracion_{identificador}.json"
                )

                shutil.copy2(archivo_actual, respaldo_anterior)

            # Reemplazar únicamente después de validar
            # y respaldar el archivo anterior.
            os.replace(temporal, archivo_actual)
            temporal = None

            # Actualizar los datos que utiliza este objeto.
            self.clientes = sistema_validacion.clientes

            return respaldo_anterior

        finally:
            # Si hubo un error, el temporal no debe quedar
            # abandonado.
            if temporal is not None:
                temporal.unlink(missing_ok=True)

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
                
                for datos_abono in datos_pedido.get('abonos', []):
                    pedido.registrar_abono(
                        datos_abono['monto'],
                        datos_abono['fecha']
                    ) 
                    
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
