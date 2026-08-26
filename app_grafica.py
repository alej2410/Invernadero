import json 
from datetime import datetime 
import customtkinter as ctk 
from tkinter import messagebox 
import uuid
import os
import hashlib
import hmac

# ========================================== 
# 0. LICENCIAS POR CLIENTE
# ==========================================
# SECRET_KEY es tuyo y de nadie más. Es lo que te permite generar claves
# válidas para cada invernadero. NUNCA lo subas a un repo público, ni lo
# compartas, ni lo cambies sin razón (si lo cambias, todas las claves que
# ya diste dejan de funcionar).
SECRET_KEY = b"DANIEL-PRIMER_PROGRAMA-LICENCIA-INVERNADERO-2026"


def obtener_id_maquina():
    """Identificador corto y estable de esta computadora (no es 100% infalible,
    pero alcanza para este caso: cambia solo si cambia la tarjeta de red)."""
    mac = str(uuid.getnode())
    return hashlib.sha256(mac.encode()).hexdigest()[:12].upper()


def generar_clave_licencia(id_maquina, nombre_cliente, secreto=SECRET_KEY):
    """Esto lo corres TÚ en tu propia PC (ver generador_licencias.py), nunca
    dentro del programa que le entregas a un cliente."""
    mensaje = f"{id_maquina.strip().upper()}:{nombre_cliente.strip().lower()}".encode()
    firma = hmac.new(secreto, mensaje, hashlib.sha256).hexdigest()[:16].upper()
    return firma


def verificar_clave_licencia(id_maquina, nombre_cliente, clave_ingresada, secreto=SECRET_KEY):
    esperada = generar_clave_licencia(id_maquina, nombre_cliente, secreto)
    return hmac.compare_digest(esperada, clave_ingresada.strip().upper())


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
                datos_cliente.get('direccion', '')
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
                    if not parte.entregado: 
                        especie = parte.especie.lower().strip() 
                        nombre_cli = cliente.nombre.title() 
                        if especie not in inventario: 
                            inventario[especie] = {"total": 0, "clientes": {}} 
                        inventario[especie]["total"] += parte.cantidad 
                        if nombre_cli not in inventario[especie]["clientes"]: 
                            inventario[especie]["clientes"][nombre_cli] = 0 
                        inventario[especie]["clientes"][nombre_cli] += parte.cantidad 
        return inventario 


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

# ========================================== 
# 2. LA VISTA (INTERFAZ GRÁFICA) 
# ========================================== 

class VentanaPrincipal(ctk.CTk): 
    def __init__(self, sistema): 
        super().__init__() 
        self.sistema = sistema 
        self.title("Sistema de Gestión - Invernadero") 
        self.geometry("700x750") 
        self.resizable(False, False) 

        self.label_titulo = ctk.CTkLabel(self, text="🌱 Gestión de Invernadero", font=("Arial", 28, "bold")) 
        self.label_titulo.pack(pady=(40, 20)) 

        self.btn_crear = ctk.CTkButton(self, text="1. Crear Cliente", height=40, font=("Arial", 14), 
                                        command=self.abrir_crear_cliente) 
        self.btn_crear.pack(pady=10, fill="x", padx=80) 

        self.btn_buscar = ctk.CTkButton(self, text="2. Buscar Cliente y Pedidos", height=40, font=("Arial", 14), 
                                        command=self.abrir_buscar_cliente) 
        self.btn_buscar.pack(pady=10, fill="x", padx=80) 

        self.btn_pedido = ctk.CTkButton(self, text="3. Crear Nuevo Pedido", height=40, font=("Arial", 14), 
                                        command=self.abrir_crear_pedido) 
        self.btn_pedido.pack(pady=10, fill="x", padx=80) 

        self.btn_reportes = ctk.CTkButton(self, text="4. Reportes e Inventario", height=40, font=("Arial", 14), 
                                          command=self.abrir_reportes) 
        self.btn_reportes.pack(pady=10, fill="x", padx=80) 

        self.btn_salir = ctk.CTkButton(self, text="Salir del Sistema", height=40, font=("Arial", 14), 
                                        fg_color="#D9534F", hover_color="#C9302C", 
                                        command=self.destroy) 
        self.btn_salir.pack(pady=(40, 10), fill="x", padx=80) 

    def validar_fecha_gui(self, fecha_str): 
        fecha_str = fecha_str.strip() 
        if not fecha_str: 
            return datetime.now().strftime("%d/%m/%Y") 
        try: 
            return datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%d/%m/%Y") 
        except ValueError: 
            return None 

    def abrir_crear_cliente(self): 
        if getattr(self, "v_crear_activa", None) and self.v_crear_activa.winfo_exists(): 
            self.v_crear_activa.focus() 
            return 
        ventana_crear = ctk.CTkToplevel(self) 
        self.v_crear_activa = ventana_crear 
        ventana_crear.title("Crear Nuevo Cliente") 
        ventana_crear.geometry("450x450") 
        ventana_crear.grab_set() 

        ctk.CTkLabel(ventana_crear, text="Registrar Cliente", font=("Arial", 20, "bold")).pack(pady=20) 

        entrada_nombre = ctk.CTkEntry(ventana_crear, placeholder_text="Nombre del cliente (*)", width=250) 
        entrada_nombre.pack(pady=10) 

        entrada_telefono = ctk.CTkEntry(ventana_crear, placeholder_text="Teléfono (*)", width=250) 
        entrada_telefono.pack(pady=10) 

        entrada_cedula = ctk.CTkEntry(ventana_crear, placeholder_text="Cédula (Opcional)", width=250)
        entrada_cedula.pack(pady=10)

        entrada_direccion = ctk.CTkEntry(ventana_crear, placeholder_text="Ubicación/Pueblo (Opcional)", width=250)
        entrada_direccion.pack(pady=10)

        label_mensaje = ctk.CTkLabel(ventana_crear, text="", font=("Arial", 12)) 
        label_mensaje.pack(pady=5) 

        def guardar_cliente(): 
            nombre = entrada_nombre.get().strip() 
            telefono = entrada_telefono.get().strip() 
            cedula = entrada_cedula.get().strip()
            direccion = entrada_direccion.get().strip()

            if not nombre or not telefono: 
                label_mensaje.configure(text="Error: Nombre y Teléfono son obligatorios.", text_color="red") 
                return 

            if self.sistema.encontrar_cliente(nombre): 
                label_mensaje.configure(text=f"Error: Ya existe '{nombre}'. Agregue un apellido.", text_color="red") 
                return 

            nuevo_cliente = Cliente(nombre, telefono, cedula, direccion) 
            self.sistema.clientes.append(nuevo_cliente) 
            self.sistema.guardar_datos() 

            label_mensaje.configure(text=f"¡Cliente '{nombre}' creado con éxito!", text_color="green") 
            
            entrada_nombre.delete(0, 'end') 
            entrada_telefono.delete(0, 'end') 
            entrada_cedula.delete(0, 'end')
            entrada_direccion.delete(0, 'end')

        btn_guardar = ctk.CTkButton(ventana_crear, text="Guardar Cliente", command=guardar_cliente) 
        btn_guardar.pack(pady=15) 

    def abrir_buscar_cliente(self): 
        if getattr(self, "v_buscar_activa", None) and self.v_buscar_activa.winfo_exists(): 
            self.v_buscar_activa.focus() 
            return 
        ventana_buscar = ctk.CTkToplevel(self) 
        self.v_buscar_activa = ventana_buscar 
        ventana_buscar.title("Directorio y Pedidos") 
        ventana_buscar.geometry("750x650")  
        ventana_buscar.grab_set() 

        frame_busqueda = ctk.CTkFrame(ventana_buscar) 
        frame_busqueda.pack(pady=20, padx=20, fill="x") 

        entrada_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar cliente (ej. luis)...", width=300) 
        entrada_busqueda.pack(side="left", padx=10, pady=10) 

        frame_resultados = ctk.CTkScrollableFrame(ventana_buscar, width=500, height=450) 
        frame_resultados.pack(pady=10, padx=20, fill="both", expand=True) 

        def mostrar_lista_clientes(lista_clientes):
            for widget in frame_resultados.winfo_children():
                widget.destroy()

            if not lista_clientes:
                ctk.CTkLabel(frame_resultados, text="No se encontraron clientes.", text_color="red").pack(pady=20)
                return

            ctk.CTkLabel(frame_resultados, text="--- Directorio de Clientes ---", font=("Arial", 16, "bold")).pack(pady=(5, 15))

            for cliente in lista_clientes:
                tarjeta = ctk.CTkFrame(frame_resultados)
                tarjeta.pack(pady=5, fill="x", padx=10)

                txt_cli = f"👤 {cliente.nombre.title()} | 📞 {cliente.telefono}"
                if cliente.cedula: txt_cli += f" | 🪪 {cliente.cedula}"
                if cliente.direccion: txt_cli += f" | 📍 {cliente.direccion}"

                ctk.CTkLabel(tarjeta, text=txt_cli, font=("Arial", 14)).pack(side="left", padx=10, pady=10)

                btn_ver = ctk.CTkButton(tarjeta, text="Ver y Gestionar Pedidos ➡", fg_color="#5bc0de", hover_color="#31b0d5", text_color="black",
                                        command=lambda c=cliente: mostrar_detalles_cliente(c))
                btn_ver.pack(side="right", padx=10, pady=10)

        def mostrar_detalles_cliente(cliente_obj):
            for widget in frame_resultados.winfo_children():
                widget.destroy()

            btn_volver = ctk.CTkButton(frame_resultados, text="⬅ Volver al Directorio", fg_color="gray", hover_color="darkgray", command=realizar_busqueda)
            btn_volver.pack(anchor="w", padx=10, pady=(0, 10))

            frame_info = ctk.CTkFrame(frame_resultados, fg_color="transparent")
            frame_info.pack(fill="x", pady=10)
            
            txt_cabecera = f"👤 {cliente_obj.nombre.title()} | 📞 {cliente_obj.telefono}"
            if cliente_obj.cedula: txt_cabecera += f" | 🪪 {cliente_obj.cedula}"
            if cliente_obj.direccion: txt_cabecera += f" | 📍 {cliente_obj.direccion}"
            ctk.CTkLabel(frame_info, text=txt_cabecera, font=("Arial", 16, "bold")).pack(side="left", padx=10)

            def abrir_editar_cliente(c_obj):
                ventana_editar = ctk.CTkToplevel(ventana_buscar)
                ventana_editar.title("Editar Cliente")
                ventana_editar.geometry("400x400")
                ventana_editar.grab_set()

                ctk.CTkLabel(ventana_editar, text="Editar Datos", font=("Arial", 16, "bold")).pack(pady=15)
                
                # Agregamos los textos de fondo (placeholders) a todos los campos
                ent_nuevo_nombre = ctk.CTkEntry(ventana_editar, width=250, placeholder_text="Nombre del cliente (*)")
                if c_obj.nombre:  # Solo inserta si hay algo guardado
                    ent_nuevo_nombre.insert(0, c_obj.nombre)
                ent_nuevo_nombre.pack(pady=10)

                ent_nuevo_tel = ctk.CTkEntry(ventana_editar, width=250, placeholder_text="Teléfono (*)")
                if c_obj.telefono:
                    ent_nuevo_tel.insert(0, c_obj.telefono)
                ent_nuevo_tel.pack(pady=10)

                ent_nueva_ced = ctk.CTkEntry(ventana_editar, width=250, placeholder_text="Cédula (Opcional)")
                if c_obj.cedula:
                    ent_nueva_ced.insert(0, c_obj.cedula)
                ent_nueva_ced.pack(pady=10)

                ent_nueva_dir = ctk.CTkEntry(ventana_editar, width=250, placeholder_text="Ubicación/Pueblo (Opcional)")
                if c_obj.direccion:
                    ent_nueva_dir.insert(0, c_obj.direccion)
                ent_nueva_dir.pack(pady=10)

                lbl_msg_edit = ctk.CTkLabel(ventana_editar, text="", font=("Arial", 12))
                lbl_msg_edit.pack(pady=5)

                def guardar_edicion():
                    n_nom = ent_nuevo_nombre.get().strip()
                    n_tel = ent_nuevo_tel.get().strip()
                    n_ced = ent_nueva_ced.get().strip()
                    n_dir = ent_nueva_dir.get().strip()

                    if not n_nom or not n_tel:
                        lbl_msg_edit.configure(text="Nombre y teléfono obligatorios.", text_color="red")
                        return
                    
                    if n_nom.lower() != c_obj.nombre.lower():
                        if self.sistema.encontrar_cliente(n_nom):
                            lbl_msg_edit.configure(text="Ya existe alguien con ese nombre.", text_color="red")
                            return
                    
                    c_obj.nombre, c_obj.telefono, c_obj.cedula, c_obj.direccion = n_nom, n_tel, n_ced, n_dir
                    self.sistema.guardar_datos()
                    ventana_editar.destroy()
                    mostrar_detalles_cliente(c_obj) 

                ctk.CTkButton(ventana_editar, text="Guardar Cambios", command=guardar_edicion).pack(pady=15)

            btn_editar = ctk.CTkButton(frame_info, text="✏️ Editar", width=60, fg_color="#f0ad4e", hover_color="#ec971f", 
                                       command=lambda: abrir_editar_cliente(cliente_obj))
            btn_editar.pack(side="right", padx=10)

            if not cliente_obj.pedidos:
                ctk.CTkLabel(frame_resultados, text="Este cliente todavía no tiene pedidos registrados.").pack(pady=10)
                return

            ctk.CTkLabel(frame_resultados, text="--- Historial de Pedidos ---", font=("Arial", 14)).pack(pady=(10, 5))

            def eliminar_pedido(c_obj, p_obj):
                if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que deseas eliminar este pedido?\nEsta acción no se puede deshacer."):
                    c_obj.pedidos.remove(p_obj)
                    self.sistema.guardar_datos()
                    mostrar_detalles_cliente(c_obj) 

            for i, pedido in enumerate(cliente_obj.pedidos, start=1):
                tarjeta_pedido = ctk.CTkFrame(frame_resultados)
                tarjeta_pedido.pack(pady=5, fill="x", padx=10)

                info_gral = f"Pedido {i} | Fecha: {pedido.fecha}\nTotal: ${pedido.calcular_total():.2f}"
                ctk.CTkLabel(tarjeta_pedido, text=info_gral, justify="left").pack(side="left", padx=10, pady=10)

                saldo_val = pedido.saldo_pendiente()
                color_saldo = "#D9534F" if saldo_val > 0 else "green"
                ctk.CTkLabel(tarjeta_pedido, text=f"Saldo Pendiente: ${saldo_val:.2f}", 
                             text_color=color_saldo, font=("Arial", 14, "bold")).pack(side="left", padx=20)

                btn_eliminar = ctk.CTkButton(tarjeta_pedido, text="🗑️", width=40, fg_color="#D9534F", hover_color="#C9302C", 
                                              command=lambda c=cliente_obj, p=pedido: eliminar_pedido(c, p))
                btn_eliminar.pack(side="right", padx=(5, 10), pady=10)

                btn_gestionar = ctk.CTkButton(tarjeta_pedido, text="Gestionar", width=80, 
                                              command=lambda p=pedido: self.abrir_gestionar_pedido(p))
                btn_gestionar.pack(side="right", padx=5, pady=10)

        def realizar_busqueda():
            busqueda = entrada_busqueda.get().strip()
            clientes_encontrados = self.sistema.encontrar_clientes_parcial(busqueda)
            clientes_ordenados = sorted(clientes_encontrados, key=lambda c: c.nombre.lower())
            mostrar_lista_clientes(clientes_ordenados)

        btn_buscar = ctk.CTkButton(frame_busqueda, text="Buscar", width=100, command=realizar_busqueda)
        btn_buscar.pack(side="left", padx=10, pady=10)

        realizar_busqueda()

    def abrir_gestionar_pedido(self, pedido): 
        if getattr(self, "v_gestion_activa", None) and self.v_gestion_activa.winfo_exists(): 
            self.v_gestion_activa.focus() 
            return 
        ventana_gestion = ctk.CTkToplevel(self) 
        self.v_gestion_activa = ventana_gestion 
        ventana_gestion.title(f"Gestionando Pedido de {pedido.cliente.nombre.title()}") 
        ventana_gestion.geometry("550x650") 
        ventana_gestion.grab_set() 

        frame_resumen = ctk.CTkFrame(ventana_gestion) 
        frame_resumen.pack(pady=15, padx=20, fill="x") 

        ctk.CTkLabel(frame_resumen, text=f"Total: ${pedido.calcular_total():.2f}", 
                     font=("Arial", 16, "bold")).pack(side="left", padx=15, pady=15) 

        color_saldo = "#D9534F" if pedido.saldo_pendiente() > 0 else "green" 
        lbl_saldo = ctk.CTkLabel(frame_resumen, text=f"Saldo: ${pedido.saldo_pendiente():.2f}", 
                                  font=("Arial", 16, "bold"), text_color=color_saldo) 
        lbl_saldo.pack(side="right", padx=15, pady=15) 

        tabview = ctk.CTkTabview(ventana_gestion) 
        tabview.pack(pady=10, padx=20, fill="both", expand=True) 

        tab_detalles = tabview.add("Detalles del Pedido") 
        tab_abonos = tabview.add("Abonos y Pagos") 
        tab_actualizar = tabview.add("Editar y Entregar") 

        scroll_detalles = ctk.CTkScrollableFrame(tab_detalles) 
        scroll_detalles.pack(fill="both", expand=True, pady=10, padx=10) 
        
        def pintar_detalles(): 
            for widget in scroll_detalles.winfo_children(): 
                widget.destroy() 
            for i, parte in enumerate(pedido.partes, start=1): 
                estado_texto = "Sí" if parte.entregado else "No" 
                fs_texto = parte.fecha_siembra if parte.fecha_siembra else "Pendiente por sembrar"
                
                info_parte = f"🌱 Parte {i}: {parte.especie.title()}\nCantidad: {parte.cantidad} | Precio: ${parte.precio:.2f}\nUbicación: {parte.ubicacion} | Siembra: {fs_texto} | ¿Entregado?: {estado_texto}" 
                if parte.fecha_estimada:
                    info_parte += f"\n📅 Entrega Estimada: {parte.fecha_estimada}"
                
                ctk.CTkLabel(scroll_detalles, text=info_parte, justify="left", 
                             fg_color=("gray85", "gray25"), corner_radius=8).pack(pady=5, fill="x", ipadx=10, ipady=10) 
        
        pintar_detalles() 

        frame_nuevo_abono = ctk.CTkFrame(tab_abonos) 
        frame_nuevo_abono.pack(pady=10, fill="x") 

        entrada_monto = ctk.CTkEntry(frame_nuevo_abono, placeholder_text="Monto ($)", width=100) 
        entrada_monto.pack(side="left", padx=10, pady=10) 

        entrada_fecha = ctk.CTkEntry(frame_nuevo_abono, placeholder_text="DD/MM/YYYY (Vacío=Hoy)", width=150) 
        entrada_fecha.pack(side="left", padx=10, pady=10) 

        lbl_msg_abono = ctk.CTkLabel(tab_abonos, text="", font=("Arial", 12)) 
        lbl_msg_abono.pack(pady=5) 

        ctk.CTkLabel(tab_abonos, text="Historial de Abonos:", font=("Arial", 14, "bold")).pack(pady=(10, 0)) 
        scroll_abonos = ctk.CTkScrollableFrame(tab_abonos) 
        scroll_abonos.pack(fill="both", expand=True, pady=10, padx=10) 

        for abono in pedido.abonos: 
            ctk.CTkLabel(scroll_abonos, text=f"📅 Fecha: {abono['fecha']}  |  💰 Monto: ${abono['monto']:.2f}").pack(pady=2, anchor="w") 

        def registrar_abono_gui(): 
            try: 
                monto = float(entrada_monto.get().strip()) 
            except ValueError: 
                lbl_msg_abono.configure(text="Error: Ingrese un monto numérico válido.", text_color="red") 
                return 

            saldo_actual = pedido.saldo_pendiente() 

            if monto <= 0: 
                lbl_msg_abono.configure(text="Error: El monto debe ser mayor a cero.", text_color="red") 
                return 
            if monto > saldo_actual: 
                lbl_msg_abono.configure(text="Error: El abono supera la deuda actual.", text_color="red") 
                return 

            fecha = self.validar_fecha_gui(entrada_fecha.get()) 
            if not fecha: 
                lbl_msg_abono.configure(text="Error: Fecha inválida. Use DD/MM/YYYY.", text_color="red") 
                return 

            pedido.registrar_abono(monto, fecha) 
            self.sistema.guardar_datos() 

            nuevo_saldo = pedido.saldo_pendiente() 
            lbl_saldo.configure(text=f"Saldo: ${nuevo_saldo:.2f}") 
            if nuevo_saldo == 0: 
                lbl_saldo.configure(text_color="green") 
            
            lbl_msg_abono.configure(text=f"¡Abono de ${monto:.2f} registrado con éxito!", text_color="green") 

            entrada_monto.delete(0, 'end') 
            entrada_fecha.delete(0, 'end') 
            ctk.CTkLabel(scroll_abonos, text=f"📅 Fecha: {fecha}  |  💰 Monto: ${monto:.2f}").pack(pady=2, anchor="w") 

        btn_abonar = ctk.CTkButton(frame_nuevo_abono, text="Abonar", command=registrar_abono_gui, width=80) 
        btn_abonar.pack(side="right", padx=10) 

        lbl_msg_actualizar = ctk.CTkLabel(tab_actualizar, text="", font=("Arial", 12)) 
        lbl_msg_actualizar.pack(pady=5) 

        scroll_actualizar = ctk.CTkScrollableFrame(tab_actualizar) 
        scroll_actualizar.pack(fill="both", expand=True, pady=5, padx=10) 

        def actualizar_parte(parte_obj, ent_ub, ent_fs, ent_fe, check_ent): 
            parte_obj.ubicacion = ent_ub.get().strip() 
            
            fs_str = ent_fs.get().strip()
            if fs_str:
                try:
                    parte_obj.fecha_siembra = datetime.strptime(fs_str, "%d/%m/%Y").strftime("%d/%m/%Y")
                except ValueError:
                    lbl_msg_actualizar.configure(text="Error: Fecha de siembra inválida (DD/MM/YYYY).", text_color="red")
                    return
            else:
                parte_obj.fecha_siembra = ""
                
            fe_str = ent_fe.get().strip()
            if fe_str:
                try:
                    parte_obj.fecha_estimada = datetime.strptime(fe_str, "%d/%m/%Y").strftime("%d/%m/%Y")
                except ValueError:
                    lbl_msg_actualizar.configure(text="Error: Fecha de entrega inválida (DD/MM/YYYY).", text_color="red")
                    return
            else:
                parte_obj.fecha_estimada = ""
            
            parte_obj.entregado = (check_ent.get() == 1) 
            
            self.sistema.guardar_datos() 
            lbl_msg_actualizar.configure(text=f"¡{parte_obj.especie.title()} actualizada!", text_color="green") 
            pintar_detalles() 

        for i, parte in enumerate(pedido.partes, start=1): 
            tarjeta = ctk.CTkFrame(scroll_actualizar, fg_color=("gray85", "gray25"), corner_radius=8) 
            tarjeta.pack(pady=5, fill="x", ipadx=10, ipady=10) 

            ctk.CTkLabel(tarjeta, text=f"🌱 Parte {i}: {parte.especie.title()} ({parte.cantidad} bandejas)", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(5, 5)) 

            fila1 = ctk.CTkFrame(tarjeta, fg_color="transparent") 
            fila1.pack(fill="x", padx=10, pady=2) 

            ctk.CTkLabel(fila1, text="Ubic.:").pack(side="left") 
            entrada_ub = ctk.CTkEntry(fila1, width=80) 
            entrada_ub.insert(0, parte.ubicacion)  
            entrada_ub.pack(side="left", padx=5) 
            
            ctk.CTkLabel(fila1, text="Siembra:").pack(side="left", padx=(5,0)) 
            entrada_fs = ctk.CTkEntry(fila1, width=95, placeholder_text="DD/MM/YYYY") 
            entrada_fs.insert(0, parte.fecha_siembra)  
            entrada_fs.pack(side="left", padx=5) 
            
            ctk.CTkLabel(fila1, text="Entrega:").pack(side="left", padx=(5,0)) 
            entrada_fe = ctk.CTkEntry(fila1, width=95, placeholder_text="DD/MM/YYYY") 
            entrada_fe.insert(0, parte.fecha_estimada)  
            entrada_fe.pack(side="left", padx=5) 

            fila2 = ctk.CTkFrame(tarjeta, fg_color="transparent") 
            fila2.pack(fill="x", padx=10, pady=5) 

            check_ent = ctk.CTkCheckBox(fila2, text="Marcar como Entregado") 
            if parte.entregado: 
                check_ent.select() 
            check_ent.pack(side="left") 

            btn_guardar_parte = ctk.CTkButton( 
                fila2, text="💾 Guardar Cambios", width=140, fg_color="#5cb85c", hover_color="#4cae4c", 
                command=lambda p=parte, u=entrada_ub, fs=entrada_fs, fe=entrada_fe, c=check_ent: actualizar_parte(p, u, fs, fe, c) 
            ) 
            btn_guardar_parte.pack(side="right")
        
    def abrir_crear_pedido(self): 
        if getattr(self, "v_pedido_activa", None) and self.v_pedido_activa.winfo_exists(): 
            self.v_pedido_activa.focus() 
            return 
        ventana_pedido = ctk.CTkToplevel(self) 
        self.v_pedido_activa = ventana_pedido 
        ventana_pedido.title("Crear Nuevo Pedido") 
        ventana_pedido.geometry("800x600")  
        ventana_pedido.grab_set() 

        estado = { 
            "cliente": None, 
            "partes_temporales": [] 
        } 

        frame_cliente = ctk.CTkFrame(ventana_pedido) 
        frame_cliente.pack(pady=10, padx=20, fill="x") 

        entrada_busqueda = ctk.CTkEntry(frame_cliente, placeholder_text="Nombre del cliente...", width=200) 
        entrada_busqueda.pack(side="left", padx=10, pady=10) 

        lbl_cliente_actual = ctk.CTkLabel(frame_cliente, text="Ningún cliente seleccionado", text_color="#D9534F", font=("Arial", 14, "bold")) 
        
        def buscar_cliente_para_pedido(): 
            nombre = entrada_busqueda.get().strip() 
            cliente = self.sistema.encontrar_cliente(nombre) 
            if cliente: 
                estado["cliente"] = cliente 
                lbl_cliente_actual.configure(text=f"Cliente Seleccionado: {cliente.nombre.title()}", text_color="green") 
            else: 
                estado["cliente"] = None 
                lbl_cliente_actual.configure(text="Cliente no encontrado", text_color="#D9534F") 

        btn_buscar_cli = ctk.CTkButton(frame_cliente, text="Buscar", width=80, command=buscar_cliente_para_pedido) 
        btn_buscar_cli.pack(side="left", padx=10) 
        lbl_cliente_actual.pack(side="left", padx=20, pady=10) 

        frame_central = ctk.CTkFrame(ventana_pedido, fg_color="transparent") 
        frame_central.pack(pady=5, padx=20, fill="both", expand=True) 

        frame_form = ctk.CTkFrame(frame_central, width=300) 
        frame_form.pack(side="left", fill="y", padx=(0, 10)) 

        ctk.CTkLabel(frame_form, text="Agregar Nueva Planta", font=("Arial", 16, "bold")).pack(pady=15) 

        ent_especie = ctk.CTkEntry(frame_form, placeholder_text="Especie (ej. Tomate)", width=220) 
        ent_especie.pack(pady=10, padx=20) 

        ent_cantidad = ctk.CTkEntry(frame_form, placeholder_text="Cantidad de bandejas", width=220) 
        ent_cantidad.pack(pady=10, padx=20) 

        ent_precio = ctk.CTkEntry(frame_form, placeholder_text="Precio por bandeja ($)", width=220) 
        ent_precio.pack(pady=10, padx=20) 

        ent_fecha = ctk.CTkEntry(frame_form, placeholder_text="Fecha Siembra (Vacío=Hoy)", width=220) 
        ent_fecha.pack(pady=10, padx=20) 

        ent_ubicacion = ctk.CTkEntry(frame_form, placeholder_text="Ubicación", width=220) 
        ent_ubicacion.pack(pady=10, padx=20) 

        ent_fecha_estimada = ctk.CTkEntry(frame_form, placeholder_text="Fecha Estimada (Opcional)", width=220)
        ent_fecha_estimada.pack(pady=10, padx=20)

        lbl_error_form = ctk.CTkLabel(frame_form, text="", text_color="red", font=("Arial", 12)) 
        lbl_error_form.pack(pady=5) 

        frame_lista = ctk.CTkFrame(frame_central) 
        frame_lista.pack(side="right", fill="both", expand=True) 

        ctk.CTkLabel(frame_lista, text="Partes del Pedido Actual", font=("Arial", 16, "bold")).pack(pady=10) 
        
        scroll_partes = ctk.CTkScrollableFrame(frame_lista) 
        scroll_partes.pack(fill="both", expand=True, padx=10, pady=5) 
        
        lbl_total_pedido = ctk.CTkLabel(frame_lista, text="Total: $0.00", font=("Arial", 18, "bold")) 
        lbl_total_pedido.pack(pady=10) 

        def refrescar_lista(): 
            for widget in scroll_partes.winfo_children(): 
                widget.destroy() 
            
            suma_total = 0 
            for i, parte in enumerate(estado["partes_temporales"], start=1): 
                texto = f"{i}. {parte.cantidad}x {parte.especie.title()} a ${parte.precio:.2f} c/u  |  Ubic: {parte.ubicacion}" 
                ctk.CTkLabel(scroll_partes, text=texto, anchor="w", fg_color="gray25", corner_radius=5).pack(fill="x", pady=2, ipadx=5, ipady=5) 
                suma_total += parte.calcular_total() 
            
            lbl_total_pedido.configure(text=f"Total: ${suma_total:.2f}") 

        def agregar_parte_al_carrito(): 
            if not estado["cliente"]: 
                lbl_error_form.configure(text="Primero busque y seleccione un cliente.", text_color="red") 
                return 

            especie = ent_especie.get().strip() 
            ubicacion = ent_ubicacion.get().strip() 
            fecha_est = ent_fecha_estimada.get().strip()
            
            try: 
                cantidad = int(ent_cantidad.get().strip()) 
                precio = float(ent_precio.get().strip()) 
                if cantidad <= 0 or precio <= 0: 
                    raise ValueError 
            except ValueError: 
                lbl_error_form.configure(text="Cantidad y Precio deben ser números > 0.", text_color="red") 
                return 

            fecha = self.validar_fecha_gui(ent_fecha.get()) 
            if not fecha: 
                lbl_error_form.configure(text="Error: Fecha inválida. Use DD/MM/YYYY.", text_color="red") 
                return 
            
            if not especie or not ubicacion: 
                lbl_error_form.configure(text="Especie y Ubicación son obligatorias.", text_color="red") 
                return 

            nueva_parte = PartePedido(especie, cantidad, precio, fecha, ubicacion, False, fecha_est) 
            estado["partes_temporales"].append(nueva_parte) 
            
            lbl_error_form.configure(text="¡Parte agregada al pedido!", text_color="green") 
            
            ent_especie.delete(0, 'end') 
            ent_cantidad.delete(0, 'end') 
            ent_precio.delete(0, 'end') 
            ent_ubicacion.delete(0, 'end') 
            ent_fecha_estimada.delete(0, 'end')
            
            refrescar_lista() 

        btn_agregar_parte = ctk.CTkButton(frame_form, text="Añadir a la lista ➡", command=agregar_parte_al_carrito) 
        btn_agregar_parte.pack(pady=10) 

        def guardar_pedido_completo(): 
            if not estado["cliente"]: 
                lbl_error_form.configure(text="No hay cliente seleccionado.", text_color="red") 
                return 
            if not estado["partes_temporales"]: 
                lbl_error_form.configure(text="Debe agregar al menos una planta.", text_color="red") 
                return 
            
            nuevo_pedido = Pedido(estado["cliente"]) 
            
            for parte in estado["partes_temporales"]: 
                nuevo_pedido.agregar_parte(parte) 
                
            estado["cliente"].pedidos.append(nuevo_pedido) 
            self.sistema.guardar_datos() 
            
            print(f"¡Pedido guardado para {estado['cliente'].nombre}!") 
            ventana_pedido.destroy() 

        btn_guardar_final = ctk.CTkButton(ventana_pedido, text="✔️ GUARDAR PEDIDO COMPLETO", height=45, 
                                          font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", 
                                          command=guardar_pedido_completo) 
        btn_guardar_final.pack(pady=15, padx=20, fill="x") 

        btn_cancelar = ctk.CTkButton(ventana_pedido, text="❌ CANCELAR Y VACIAR", height=45, 
                                      font=("Arial", 16, "bold"), fg_color="#D9534F", hover_color="#C9302C", 
                                      command=ventana_pedido.destroy) 
        btn_cancelar.pack(pady=(0, 15), padx=20, fill="x") 
        
    def abrir_reportes(self): 
        if getattr(self, "v_reportes_activa", None) and self.v_reportes_activa.winfo_exists(): 
            self.v_reportes_activa.focus() 
            return 
        ventana_reportes = ctk.CTkToplevel(self) 
        self.v_reportes_activa = ventana_reportes 
        ventana_reportes.title("Reportes y Consultas") 
        ventana_reportes.geometry("550x650") 
        ventana_reportes.grab_set() 

        ctk.CTkLabel(ventana_reportes, text="📊 Panel de Reportes", font=("Arial", 22, "bold")).pack(pady=15) 

        tabview = ctk.CTkTabview(ventana_reportes) 
        tabview.pack(pady=10, padx=20, fill="both", expand=True) 

        tab_deudores = tabview.add("Deudores") 
        tab_inventario = tabview.add("Inventario Activo") 

        deudores, total_deuda = self.sistema.reporte_deudores() 
        
        frame_total_deuda = ctk.CTkFrame(tab_deudores, fg_color="#D9534F") 
        frame_total_deuda.pack(fill="x", padx=10, pady=10) 
        ctk.CTkLabel(frame_total_deuda, text=f"Total por Cobrar: ${total_deuda:.2f}", 
                     font=("Arial", 18, "bold"), text_color="white").pack(pady=10) 

        scroll_deudores = ctk.CTkScrollableFrame(tab_deudores) 
        scroll_deudores.pack(fill="both", expand=True, padx=10, pady=5) 

        if not deudores: 
            ctk.CTkLabel(scroll_deudores, text="¡Felicidades! Ningún cliente tiene deudas.", 
                         font=("Arial", 14), text_color="green").pack(pady=20) 
        else: 
            for d in deudores: 
                texto = f"👤 Cliente: {d['nombre'].title()} | Tel: {d['telefono']}\nDeuda Actual: ${d['deuda']:.2f}" 
                
                if d['plantas']: 
                    texto_plantas = " | ".join([f"{cant}x {esp.title()}" for esp, cant in d['plantas'].items()]) 
                    texto += f"\n📦 Esperando: {texto_plantas}" 
                else: 
                    texto += f"\n📦 (No tiene bandejas activas pendientes)" 

                ctk.CTkLabel(scroll_deudores, text=texto, anchor="w", justify="left", 
                             fg_color=("gray85", "gray25"), corner_radius=5).pack(fill="x", pady=5, ipadx=10, ipady=10) 

        inventario = self.sistema.reporte_inventario_activo() 
        total_bandejas = sum(datos["total"] for datos in inventario.values()) 

        frame_total_inv = ctk.CTkFrame(tab_inventario, fg_color="green") 
        frame_total_inv.pack(fill="x", padx=10, pady=10) 
        ctk.CTkLabel(frame_total_inv, text=f"Bandejas Totales en Invernadero: {total_bandejas}", 
                     font=("Arial", 18, "bold"), text_color="white").pack(pady=10) 

        scroll_inventario = ctk.CTkScrollableFrame(tab_inventario) 
        scroll_inventario.pack(fill="both", expand=True, padx=10, pady=5) 

        if not inventario: 
            ctk.CTkLabel(scroll_inventario, text="No hay bandejas activas.", font=("Arial", 14)).pack(pady=20) 
        else: 
            for especie, datos in sorted(inventario.items()): 
                texto = f"🌿 Especie: {especie.title()}  👉  TOTAL: {datos['total']} bandejas\n" 
                
                lista_clientes = [] 
                for cli, cant in datos["clientes"].items(): 
                    lista_clientes.append(f"      ↳ {cli}: {cant}") 
                
                texto += "\n".join(lista_clientes) 

                ctk.CTkLabel(scroll_inventario, text=texto, anchor="w", justify="left", 
                             fg_color=("gray85", "gray25"), corner_radius=5).pack(fill="x", pady=5, ipadx=10, ipady=10) 

# ========================================== 

# ========================================== 
# 3. EL CONTROLADOR (MAIN) CON SEGURIDAD POR CLIENTE
# ========================================== 
def main():
    archivo_licencia = "licencia.key"
    id_maquina = obtener_id_maquina()

    def cargar_licencia():
        if os.path.exists(archivo_licencia):
            try:
                with open(archivo_licencia, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None
        return None

    datos_licencia = cargar_licencia()
    licencia_valida = (
        datos_licencia is not None
        and datos_licencia.get('id_maquina') == id_maquina
        and verificar_clave_licencia(
            id_maquina, datos_licencia.get('nombre_cliente', ''), datos_licencia.get('clave', '')
        )
    )

    if licencia_valida:
        iniciar_programa(datos_licencia.get('nombre_cliente', ''))
        return

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")

    ventana_login = ctk.CTk()
    ventana_login.title("Activación de Software")
    ventana_login.geometry("440x340")
    ventana_login.resizable(False, False)

    ctk.CTkLabel(ventana_login, text="Sistema Protegido", font=("Arial", 22, "bold")).pack(pady=(25, 5))
    ctk.CTkLabel(
        ventana_login,
        text=f"ID de esta computadora:\n{id_maquina}",
        font=("Consolas", 13, "bold"),
        justify="center",
    ).pack(pady=(5, 15))
    ctk.CTkLabel(
        ventana_login,
        text="Envía ese ID al desarrollador para recibir tu clave.",
        font=("Arial", 11),
        text_color="gray",
    ).pack(pady=(0, 10))

    ctk.CTkLabel(ventana_login, text="Nombre del invernadero:").pack(pady=(5, 0))
    entrada_nombre = ctk.CTkEntry(ventana_login, width=260)
    entrada_nombre.pack(pady=5)

    ctk.CTkLabel(ventana_login, text="Clave de licencia:").pack(pady=(5, 0))
    entrada_clave = ctk.CTkEntry(ventana_login, width=260)
    entrada_clave.pack(pady=5)

    lbl_error = ctk.CTkLabel(ventana_login, text="", text_color="red")
    lbl_error.pack(pady=(5, 0))

    def verificar():
        nombre = entrada_nombre.get().strip()
        clave = entrada_clave.get().strip()
        if not nombre or not clave:
            lbl_error.configure(text="Completa ambos campos.")
            return
        if verificar_clave_licencia(id_maquina, nombre, clave):
            with open(archivo_licencia, 'w', encoding='utf-8') as f:
                json.dump({'id_maquina': id_maquina, 'nombre_cliente': nombre, 'clave': clave}, f)
            ventana_login.destroy()
            iniciar_programa(nombre)
        else:
            lbl_error.configure(text="Clave incorrecta para este invernadero/computadora.")

    ctk.CTkButton(ventana_login, text="Activar", command=verificar).pack(pady=15)
    ventana_login.mainloop()


def iniciar_programa(nombre_cliente=""):
    sistema = SistemaInvernadero() 
    ctk.set_appearance_mode("System") 
    ctk.set_default_color_theme("green") 
    app = VentanaPrincipal(sistema)
    if nombre_cliente:
        app.title(f"Sistema de Gestión - Invernadero  |  Licenciado a: {nombre_cliente}")
    app.mainloop() 

if __name__ == "__main__": 
    main()