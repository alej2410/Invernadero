import json
import customtkinter as ctk
import os
from rutas import obtener_ruta_datos
from modelos import Cliente, PartePedido, Pedido
from tkinter import filedialog, messagebox
from datetime import datetime
from sistema import SistemaInvernadero
from licencias import obtener_id_maquina, verificar_clave_licencia
from validaciones import validar_fecha_opcional
from decimal import Decimal, InvalidOperation
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

        self.btn_copia = ctk.CTkButton(self, text="5. Crear Copia de Seguridad", height=40, font=("Arial", 14),
                                        command=self.crear_copia_desde_gui)
        self.btn_copia.pack(pady=10, fill="x", padx=80)

        self.btn_restaurar = ctk.CTkButton(self, text="6. Restaurar Copia de Seguridad", height=40, font=("Arial", 14),
                                        command=self.restaurar_copia_desde_gui)
        self.btn_restaurar.pack(pady=10, fill="x", padx=80)

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

        ventana_crear.title("Registrar Cliente")
        ventana_crear.geometry("480x560")
        ventana_crear.minsize(380, 420)
        ventana_crear.resizable(True, True)
        ventana_crear.grab_set()

        # Contenedor adaptable con desplazamiento vertical.
        contenido = ctk.CTkScrollableFrame(ventana_crear)
        contenido.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        contenido.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenido,
            text="Registrar Cliente",
            font=("Arial", 22, "bold")
        ).grid(row=0, column=0, pady=(10, 25))

        def crear_campo(fila, etiqueta, ejemplo):
            ctk.CTkLabel(
                contenido,
                text=etiqueta,
                anchor="w"
            ).grid(
                row=fila,
                column=0,
                sticky="ew",
                padx=10,
                pady=(8, 2)
            )

            entrada = ctk.CTkEntry(
                contenido,
                placeholder_text=ejemplo,
                height=35
            )
            entrada.grid(
                row=fila + 1,
                column=0,
                sticky="ew",
                padx=10,
                pady=(0, 8)
            )

            return entrada

        entrada_nombre = crear_campo(
            1, "Nombre del cliente *", "Ej. José Pérez"
        )

        entrada_telefono = crear_campo(
            3, "Teléfono *", "Ej. 04141234567"
        )

        entrada_cedula = crear_campo(
            5, "Cédula (opcional)", "Ej. V-12345678"
        )

        entrada_direccion = crear_campo(
            7, "Ubicación / Pueblo (opcional)", "Ej. Venegara"
        )

        label_mensaje = ctk.CTkLabel(
            contenido,
            text="",
            font=("Arial", 12),
            wraplength=300
        )
        label_mensaje.grid(
            row=9,
            column=0,
            sticky="ew",
            padx=10,
            pady=10
        )

        def guardar_cliente():
            nombre = entrada_nombre.get().strip()
            telefono = entrada_telefono.get().strip()
            cedula = entrada_cedula.get().strip()
            direccion = entrada_direccion.get().strip()

            if not nombre or not telefono:
                label_mensaje.configure(
                    text="Nombre y teléfono son obligatorios.",
                    text_color="red"
                )
                return

            nuevo_cliente = Cliente(
                nombre, telefono, cedula, direccion
            )

            self.sistema.clientes.append(nuevo_cliente)
            self.sistema.guardar_datos()

            label_mensaje.configure(
                text=f"¡Cliente '{nombre}' creado con éxito!",
                text_color="green"
            )

            for entrada in (
                entrada_nombre,
                entrada_telefono,
                entrada_cedula,
                entrada_direccion
            ):
                entrada.delete(0, "end")

            entrada_nombre.focus_set()

        ctk.CTkButton(
            contenido,
            text="Guardar Cliente",
            height=42,
            command=guardar_cliente
        ).grid(
            row=10,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 20)
        )

        entrada_nombre.focus_set()
   

    def crear_copia_desde_gui(self):
        carpeta = filedialog.askdirectory(
            parent=self,
            title="Selecciona dónde guardar la copia de seguridad",
            mustexist=True
        )

        # Cancelar el selector no debe crear ningún archivo.
        if not carpeta:
            return

        try:
            copia = self.sistema.crear_copia_seguridad(
                carpeta_destino=carpeta
            )
        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror(
                "No se pudo crear la copia",
                f"No se creó ninguna copia de seguridad.\n\n{error}",
                parent=self
            )
            return

        messagebox.showinfo(
            "Copia creada",
            f"La copia de seguridad se guardó en:\n\n{copia}",
            parent=self
        )


    def restaurar_copia_desde_gui(self):
        # Evitar que otras ventanas con datos antiguos sigan abiertas.
        ventanas_abiertas = [
            ventana
            for ventana in self.winfo_children()
            if isinstance(ventana, ctk.CTkToplevel)
            and ventana.winfo_exists()
        ]

        if ventanas_abiertas:
            messagebox.showwarning(
                "Cierra las ventanas abiertas",
                "Antes de restaurar, cierra las ventanas de "
                "clientes, pedidos y reportes.",
                parent=self
            )
            return

        ruta_copia = filedialog.askopenfilename(
            parent=self,
            title="Selecciona la copia que deseas restaurar",
            filetypes=[
                ("Archivos JSON", "*.json"),
                ("Todos los archivos", "*.*")
            ]
        )

        # Si el usuario cancela, no modificar nada.
        if not ruta_copia:
            return

        confirmar = messagebox.askyesno(
            "Confirmar restauración",
            "¿Quieres reemplazar los datos actuales por "
            "los de esta copia?\n\n"
            "El programa intentará guardar una copia de "
            "los datos actuales antes de reemplazarlos.\n\n"
            f"Archivo seleccionado:\n{ruta_copia}",
            parent=self
        )

        if not confirmar:
            return

        try:
            respaldo_anterior = (
                self.sistema.restaurar_copia_seguridad(ruta_copia)
            )
        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror(
                "No se pudo restaurar",
                "Los datos actuales no se reemplazaron.\n\n"
                f"Detalle: {error}",
                parent=self
            )
            return

        mensaje = "La copia se restauró correctamente."

        if respaldo_anterior is not None:
            mensaje += (
                "\n\nLos datos que tenías antes quedaron en:\n"
                f"{respaldo_anterior}"
            )

        messagebox.showinfo(
            "Restauración completada",
            mensaje,
            parent=self
        )

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
                monto = Decimal(entrada_monto.get().strip()) 
            except (ValueError, InvalidOperation): 
                lbl_msg_abono.configure(text="Error: Ingrese un monto numérico válido.", text_color="red") 
                return 

            saldo_actual = pedido.saldo_pendiente() 

            if not monto.is_finite():
                lbl_msg_abono.configure(
                    text="Error: Ingrese un monto válido.",
                    text_color="red"
                    )
                return

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

            # 1. Leer todos los campos sin modificar el pedido.
            nueva_ubicacion = ent_ub.get().strip()
            nueva_fecha_siembra = ent_fs.get().strip()
            nueva_fecha_entrega = ent_fe.get().strip()
            nuevo_estado = check_ent.get() == 1

            # 2. Validar la fecha de siembra.
            if nueva_fecha_siembra:
                try:
                    nueva_fecha_siembra = datetime.strptime(
                        nueva_fecha_siembra, "%d/%m/%Y"
                    ).strftime("%d/%m/%Y")

                except ValueError:
                    lbl_msg_actualizar.configure(
                        text="Error: Fecha de siembra inválida (DD/MM/YYYY).",
                        text_color="red"
                    )
                    return

            # 3. Validar la fecha estimada de entrega.
            if nueva_fecha_entrega:
                try:
                    nueva_fecha_entrega = datetime.strptime(
                        nueva_fecha_entrega, "%d/%m/%Y"
                    ).strftime("%d/%m/%Y")

                except ValueError:
                    lbl_msg_actualizar.configure(
                        text="Error: Fecha de entrega inválida (DD/MM/YYYY).",
                        text_color="red"
                    )
                    return

            # 4. Todas las validaciones pasaron.
            # Ahora sí modificamos los datos.
            parte_obj.ubicacion = nueva_ubicacion
            parte_obj.fecha_siembra = nueva_fecha_siembra
            parte_obj.fecha_estimada = nueva_fecha_entrega
            parte_obj.entregado = nuevo_estado

            # 5. Guardar los cambios.
            self.sistema.guardar_datos()

            lbl_msg_actualizar.configure(
                text=f"¡{parte_obj.especie.title()} actualizada!",
                text_color="green"
            )

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

        
        # Buscador de clientes
        frame_busqueda = ctk.CTkFrame(
            frame_cliente,
            fg_color="transparent"
        )
        frame_busqueda.pack(fill="x")

        texto_busqueda = ctk.StringVar()

        entrada_busqueda = ctk.CTkEntry(
            frame_busqueda,
            placeholder_text="Buscar cliente por nombre...",
            textvariable=texto_busqueda,
            width=220
        )
        entrada_busqueda.pack(side="left", padx=10, pady=10)

        lbl_cliente_actual = ctk.CTkLabel(
            frame_busqueda,
            text="Ningún cliente seleccionado",
            text_color="#D9534F",
            font=("Arial", 13, "bold")
        )
        lbl_cliente_actual.pack(side="left", padx=10)

        # Lista desplegable de coincidencias
        frame_resultados_clientes = ctk.CTkScrollableFrame(
            frame_cliente,
            height=110
        )

        def seleccionar_cliente(cliente):
            # Guardamos el objeto real, no solamente su nombre.
            estado["cliente"] = cliente

            lbl_cliente_actual.configure(
                text=f"Seleccionado: {cliente.nombre.title()}",
                text_color="green"
            )

            # Ocultar la lista después de seleccionar.
            frame_resultados_clientes.pack_forget()

        def actualizar_busqueda(*args):
            # Si el trabajador modifica la búsqueda,
            # debe seleccionar nuevamente un cliente.
            estado["cliente"] = None

            lbl_cliente_actual.configure(
                text="Ningún cliente seleccionado",
                text_color="#D9534F"
            )

            # Limpiar los resultados anteriores.
            for widget in frame_resultados_clientes.winfo_children():
                widget.destroy()

            busqueda = texto_busqueda.get().strip()

            if not busqueda:
                frame_resultados_clientes.pack_forget()
                return

            # Reutilizamos la búsqueda parcial existente.
            resultados = self.sistema.encontrar_clientes_parcial(
                busqueda
            )

            resultados = sorted(
                resultados,
                key=lambda cliente: cliente.nombre.lower()
            )

            # Mostrar la lista.
            frame_resultados_clientes.pack(
                fill="x",
                padx=10,
                pady=(0, 10)
            )

            if not resultados:
                ctk.CTkLabel(
                    frame_resultados_clientes,
                    text="No se encontraron clientes."
                ).pack(pady=10)
                return

            # Crear un botón por cada cliente encontrado.
            for cliente in resultados:
                informacion = (
                    f"{cliente.nombre.title()}\n"
                    f"Tel: {cliente.telefono}"
                )

                if cliente.direccion:
                    informacion += f" | {cliente.direccion}"

                ctk.CTkButton(
                    frame_resultados_clientes,
                    text=informacion,
                    height=45,
                    anchor="w",
                    command=lambda c=cliente: seleccionar_cliente(c)
                ).pack(
                    fill="x",
                    padx=5,
                    pady=3
                )

        # Actualizar resultados cada vez que cambie el texto.
        texto_busqueda.trace_add("write", actualizar_busqueda)

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
            
            try: 
                cantidad = int(ent_cantidad.get().strip()) 
                precio = Decimal(ent_precio.get().strip())
                if not precio.is_finite():
                    raise ValueError
                if cantidad <= 0 or precio <= 0: 
                    raise ValueError 
            except (ValueError, InvalidOperation): 
                lbl_error_form.configure(text="Cantidad y Precio deben ser números > 0.", text_color="red") 
                return 

            fecha = self.validar_fecha_gui(ent_fecha.get()) 
            if not fecha: 
                lbl_error_form.configure(text="Error: Fecha inválida. Use DD/MM/YYYY.", text_color="red") 
                return 
            
            # Validar fecha estimada de entrega.
            try:
                fecha_est = validar_fecha_opcional(
                    ent_fecha_estimada.get()
                )

            except ValueError:
                lbl_error_form.configure(
                    text="Error: Fecha estimada inválida. Use DD/MM/YYYY.",
                    text_color="red"
                )
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

                for cliente_id, info in datos["clientes"].items():

                    nombre = info["nombre"].title()
                    telefono = info["telefono"]
                    cantidad = info["cantidad"]

                    lista_clientes.append(
                        f"      ↳ {nombre} "
                        f"(Tel: {telefono}): {cantidad}"
                    ) 
                
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
    ventana_login.geometry("440x450")
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
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")

    ruta_datos = obtener_ruta_datos()

    while True:
        try:
            sistema = SistemaInvernadero(archivo_datos=ruta_datos)

        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            InvalidOperation
        ) as error:

            # No abrir el sistema normal si falló la carga.
            ventana = ctk.CTk()
            ventana.title("Recuperación de datos")
            ventana.geometry("540x350")
            ventana.resizable(False, False)

            restaurado = {"valor": False}

            ctk.CTkLabel(
                ventana,
                text="No se pudieron cargar los datos",
                font=("Arial", 21, "bold")
            ).pack(pady=(25, 12))

            ctk.CTkLabel(
                ventana,
                text=(
                    "El archivo de datos no se pudo leer correctamente.\n"
                    "No se modificará ni se reemplazará automáticamente.\n\n"
                    "Selecciona una copia de seguridad para recuperarlo,\n"
                    "o cierra el programa."
                ),
                justify="center"
            ).pack(padx=20, pady=(0, 12))

            def seleccionar_copia():
                carpeta_copias = ruta_datos.parent / "copias_seguridad"

                carpeta_inicial = (
                    carpeta_copias
                    if os.path.isdir(carpeta_copias)
                    else os.getcwd()
                )

                ruta = filedialog.askopenfilename(
                    parent=ventana,
                    title="Selecciona una copia de seguridad",
                    initialdir=carpeta_inicial,
                    filetypes=[
                        ("Archivos JSON", "*.json"),
                        ("Todos los archivos", "*.*")
                    ]
                )

                if not ruta:
                    return

                confirmar = messagebox.askyesno(
                    "Confirmar recuperación",
                    "¿Quieres restaurar esta copia?\n\n"
                    "El programa intentará conservar el archivo "
                    "actual antes de reemplazarlo.\n\n"
                    f"Archivo seleccionado:\n{ruta}",
                    parent=ventana
                )

                if not confirmar:
                    return

                try:
                    # Crear un objeto sin cargar el JSON dañado.
                    recuperador = SistemaInvernadero(
                        archivo_datos=ruta_datos,
                        cargar=False
                    )

                    respaldo_anterior = (
                        recuperador.restaurar_copia_seguridad(ruta)
                    )

                    # Comprobar que el próximo inicio puede cargarlo.
                    SistemaInvernadero(archivo_datos=ruta_datos)

                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    AttributeError,
                    InvalidOperation
                ) as error_recuperacion:
                    messagebox.showerror(
                        "Error de recuperación",
                        "No se pudo completar la recuperación.\n\n"
                        f"Detalle: {error_recuperacion}",
                        parent=ventana
                    )
                    return

                mensaje = "Los datos se recuperaron correctamente."

                if respaldo_anterior is not None:
                    mensaje += (
                        "\n\nEl archivo que se reemplazó "
                        "quedó guardado en:\n"
                        f"{respaldo_anterior}"
                    )

                messagebox.showinfo(
                    "Recuperación completada",
                    mensaje,
                    parent=ventana
                )

                restaurado["valor"] = True
                ventana.destroy()

            ctk.CTkButton(
                ventana,
                text="Seleccionar copia de seguridad",
                height=40,
                command=seleccionar_copia
            ).pack(fill="x", padx=75, pady=(8, 10))

            ctk.CTkButton(
                ventana,
                text="Salir sin modificar los datos",
                height=40,
                fg_color="#D9534F",
                hover_color="#C9302C",
                command=ventana.destroy
            ).pack(fill="x", padx=75, pady=(0, 15))

            ventana.mainloop()

            if not restaurado["valor"]:
                return

            # Tras restaurar, volver a intentar el inicio normal.
            continue

        # Solo llegamos aquí si los datos se cargaron correctamente.
        app = VentanaPrincipal(sistema)

        if nombre_cliente:
            app.title(
                "Sistema de Gestión - Invernadero"
                f"  |  Licenciado a: {nombre_cliente}"
            )

        app.mainloop()
        return

if __name__ == "__main__": 
    main()