
# 🌱 Sistema de Gestión para Invernadero

Aplicación de escritorio desarrollada en Python para digitalizar la gestión de clientes, pedidos, siembras, entregas y pagos de un invernadero.

El proyecto surge de una necesidad real: reemplazar los registros en cuadernos físicos por un sistema que permita consultar y organizar la información de manera más sencilla.

Actualmente funciona de forma local, con una interfaz gráfica desarrollada en CustomTkinter y almacenamiento en JSON.

## Funcionalidades

### Gestión de clientes

- Registro de clientes con nombre, teléfono, cédula y ubicación.
- Búsqueda parcial por nombre.
- Edición de información.
- Identificadores únicos (UUID).
- Soporte para clientes con nombres repetidos.
- Consulta del historial de pedidos.

### Gestión de pedidos

Cada cliente puede tener múltiples pedidos, y cada pedido puede contener diferentes especies de plantas.

Para cada parte del pedido se registra:

- Especie.
- Cantidad de bandejas.
- Precio por bandeja.
- Fecha de siembra.
- Fecha estimada de entrega.
- Ubicación dentro del invernadero.
- Estado de entrega.

El sistema permite actualizar las fechas, la ubicación y el estado de entrega de cada parte del pedido.

### Pagos y abonos

- Cálculo automático del total de cada pedido.
- Registro de abonos parciales.
- Historial de pagos.
- Cálculo del saldo pendiente.
- Validación para impedir abonos superiores al saldo.

Los importes se manejan mediante `Decimal` para evitar los errores de representación propios de los números de punto flotante.

### Reportes

**Deudores**

Permite consultar los clientes con saldos pendientes, sus deudas individuales y el total global por cobrar.

**Inventario activo**

Muestra las bandejas que todavía no han sido entregadas, agrupadas por especie y cliente.

Los clientes se distinguen internamente mediante UUID para evitar que se mezclen las cantidades de personas con nombres idénticos.

## Tecnologías

| Tecnología | Utilización |
|---|---|
| Python | Lenguaje principal |
| CustomTkinter | Interfaz gráfica |
| Tkinter | Cuadros de diálogo |
| JSON | Persistencia local |
| Decimal | Cálculos monetarios |
| UUID | Identificación de clientes |
| pytest | Pruebas automatizadas |

El proyecto utiliza también módulos de la biblioteca estándar de Python para la gestión de archivos, fechas y licencias.

## Estructura del proyecto

```text
Invernadero/
│
├── app_grafica.py
├── modelos.py
├── sistema.py
├── validaciones.py
├── licencias.py
│
├── tests/
│   ├── test_clientes.py
│   ├── test_dinero.py
│   ├── test_fechas.py
│   ├── test_guardado_seguro.py
│   ├── test_inventario.py
│   ├── test_pedidos.py
│   └── test_persistencia.py
│
├── README.md
├── .gitignore
└── .gitattributes
```

### Organización del código

- `app_grafica.py`: interfaz gráfica y arranque de la aplicación.
- `modelos.py`: clases Cliente, Pedido y PartePedido.
- `sistema.py`: gestión de clientes, persistencia y reportes.
- `validaciones.py`: validación de fechas opcionales.
- `licencias.py`: funciones de identificación del equipo y verificación de licencias.
- `tests/`: pruebas automatizadas de la lógica y la persistencia.

## Instalación para desarrollo

### 1. Clonar el repositorio

```bash
git clone https://github.com/alej2410/Invernadero.git
cd Invernadero
```

### 2. Crear un entorno virtual

```bash
python -m venv .venv
```

En Windows, activarlo con:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install customtkinter pytest cryptography
```

### 4. Ejecutar la aplicación

```bash
python app_grafica.py
```

La aplicación requiere una licencia válida para acceder a sus funcionalidades.

## Pruebas automatizadas

El proyecto utiliza `pytest` para comprobar diferentes comportamientos del sistema.

Ejecutar todas las pruebas:

```bash
python -m pytest -v
```

Las pruebas actuales cubren:

- Cálculos de pedidos.
- Registro y cálculo de abonos.
- Persistencia de datos.
- Identificadores únicos.
- Independencia de clientes con nombres repetidos.
- Inventario activo.
- Validación de fechas.
- Conservación de importes decimales.
- Manejo de errores durante el guardado de archivos.

Las pruebas de persistencia utilizan directorios temporales para evitar modificar los datos locales del usuario.

## Persistencia

La aplicación almacena su información en:

```text
datos_invernadero.json
```

El archivo contiene los clientes, sus pedidos y sus abonos.

Los importes monetarios se guardan como cadenas decimales y se recuperan como objetos `Decimal`.

### Guardado seguro

El sistema utiliza archivos temporales y `os.replace()` para evitar sobrescribir directamente el JSON original durante la escritura.

Si ocurre un error antes de completar el reemplazo, se conserva el archivo anterior.

Este mecanismo no sustituye un sistema de copias de seguridad.

El archivo de datos y la licencia local están excluidos del repositorio mediante `.gitignore`.

## Activación

La aplicación dispone de un mecanismo de activación local asociado al identificador del equipo.

Para activar una instalación se necesita una licencia proporcionada por el desarrollador.

El mecanismo de licencias se encuentra en revisión y no debe considerarse una protección resistente frente a la ingeniería inversa.

Las licencias utilizan firmas digitales Ed25519. La aplicación contiene una clave pública para verificarlas; la clave privada y el generador se mantienen fuera del repositorio y del programa distribuido.

## Estado y alcance

El proyecto se encuentra en desarrollo.

Actualmente:

- Es una aplicación de escritorio.
- Funciona localmente.
- No requiere Internet para gestionar los datos.
- No dispone de sincronización entre equipos.
- No utiliza una base de datos SQL.
- No incluye una interfaz web.

La aplicación ha sido desarrollada y probada en Windows con Python 3.14.

## Próximas mejoras

- Fortalecer el sistema de licencias.
- Incorporar copias de seguridad y restauración.
- Ampliar las validaciones de datos.
- Mejorar la distribución e instalación.
- Continuar ampliando las pruebas automatizadas.

Otras funcionalidades se evaluarán según las necesidades que surjan durante el uso del sistema.

## Origen del proyecto

Este proyecto nació a partir de una necesidad de un familiar que administra un invernadero y buscaba una alternativa a los registros manuales de clientes y pedidos.

Además de resolver ese problema, el desarrollo constituye una oportunidad de aprendizaje práctico en programación orientada a objetos, diseño de software, persistencia, pruebas automatizadas y control de versiones.