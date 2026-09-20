# 🌱 Sistema de Gestión para Invernadero

Aplicación de escritorio desarrollada en Python para facilitar la administración diaria de un invernadero.

El sistema permite gestionar clientes, pedidos de plantas, fechas de siembra y entrega, pagos pendientes e inventario activo desde una interfaz gráfica sencilla.

Actualmente funciona de forma local y almacena la información en un archivo JSON.

## ✨ Funcionalidades

### 👥 Gestión de clientes

* Registrar nuevos clientes.
* Guardar nombre, teléfono, cédula y ubicación.
* Buscar clientes por nombre.
* Editar la información de clientes existentes.
* Consultar el historial completo de pedidos de cada cliente.

### 📦 Gestión de pedidos

Cada cliente puede tener múltiples pedidos y cada pedido puede contener diferentes tipos de plantas.

Para cada parte del pedido se registra:

* Especie.
* Cantidad de bandejas.
* Precio por bandeja.
* Fecha de siembra.
* Fecha estimada de entrega.
* Ubicación dentro del invernadero.
* Estado de entrega.

También es posible actualizar posteriormente la ubicación, las fechas y marcar las plantas como entregadas.

### 💰 Pagos y abonos

El sistema permite:

* Registrar abonos parciales.
* Mantener un historial de pagos.
* Calcular automáticamente el total de cada pedido.
* Consultar cuánto ha pagado el cliente.
* Calcular el saldo pendiente.

El sistema evita registrar abonos superiores a la deuda actual del pedido.

### 📊 Reportes

Actualmente se incluyen dos reportes principales.

#### Deudores

Permite consultar:

* Clientes con saldo pendiente.
* Deuda individual.
* Total global por cobrar.
* Plantas pendientes asociadas al cliente.

#### Inventario activo

Muestra todas las bandejas que todavía no han sido entregadas, agrupadas por especie y cliente.

Esto permite conocer rápidamente cuántas bandejas permanecen activas dentro del invernadero.

## 🔐 Activación

La aplicación incorpora un sistema de activación local asociado al equipo donde se instala.

Al ejecutarse por primera vez muestra un identificador de la computadora y solicita:

* Nombre del invernadero.
* Clave de licencia.

Una vez activado correctamente, los datos de activación se almacenan localmente.

## 🛠️ Tecnologías

* **Python 3**
* **CustomTkinter** — interfaz gráfica
* **Tkinter** — cuadros de diálogo
* **JSON** — persistencia local
* **HMAC / SHA-256** — mecanismo actual de validación de licencias

El resto de los módulos utilizados pertenecen a la biblioteca estándar de Python.

## 📁 Estructura actual

```text
Invernadero/
│
├── app_grafica.py
├── README.md
├── .gitignore
└── .gitattributes
```

`app_grafica.py` contiene actualmente la lógica del sistema, modelos de datos, persistencia, interfaz gráfica y sistema de activación.

## 🚀 Instalación para desarrollo

Clona el repositorio:

```bash
git clone https://github.com/alej2410/Invernadero.git
cd Invernadero
```

Crea un entorno virtual:

```bash
python -m venv .venv
```

Actívalo en Windows:

```bash
.venv\Scripts\activate
```

Instala CustomTkinter:

```bash
pip install customtkinter
```

Ejecuta la aplicación:

```bash
python app_grafica.py
```

## 💾 Persistencia de datos

Los datos se almacenan localmente en:

```text
datos_invernadero.json
```

Este archivo contiene clientes, pedidos, partes de pedidos y abonos.

El archivo se encuentra excluido del repositorio mediante `.gitignore`, por lo que los datos reales de cada instalación no se publican accidentalmente en GitHub.

El archivo local de licencia también se encuentra excluido.

## 🖥️ Alcance actual

La versión actual está diseñada como una aplicación de escritorio para utilizarse localmente en un invernadero.

Actualmente:

* Funciona en una sola computadora.
* Utiliza almacenamiento JSON local.
* No requiere conexión a Internet.
* No utiliza servidor.
* No utiliza base de datos externa.
* No incluye todavía sincronización entre dispositivos.

## 📌 Estado del proyecto

El proyecto se encuentra en desarrollo activo.

La versión actual constituye una primera implementación funcional para digitalizar tareas que normalmente se realizan manualmente, como el seguimiento de clientes, pedidos, siembras, entregas, pagos e inventario.
