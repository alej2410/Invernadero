
# 🌱 Sistema de Gestión para Invernadero

Aplicación de escritorio desarrollada en Python para gestionar clientes, pedidos, siembras, entregas y pagos de un invernadero.

El proyecto surge de una necesidad planteada por un familiar: sustituir los registros en cuadernos por un sistema que facilite organizar y consultar la información. Actualmente se desarrolla como proyecto de aprendizaje y portafolio; no se ha desplegado para uso operativo.

Funciona de manera local, con una interfaz gráfica desarrollada en CustomTkinter y almacenamiento en JSON.

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

Los importes se manejan mediante `Decimal` para evitar errores de representación propios de los números de punto flotante.

### Reportes

**Deudores:** permite consultar los clientes con saldos pendientes, sus deudas individuales y el total global por cobrar.

**Inventario activo:** muestra las bandejas que todavía no han sido entregadas, agrupadas por especie y cliente.

Los clientes se distinguen internamente mediante UUID para evitar que se mezclen las cantidades de personas con nombres idénticos.

### Copias de seguridad y recuperación

- Creación de copias de seguridad desde la interfaz gráfica.
- Selección de la carpeta donde se guardará cada copia.
- Restauración de una copia mediante un selector de archivos y una confirmación.
- Conservación del archivo reemplazado antes de completar una restauración.
- Validación de las copias antes de utilizarlas.
- Detección de errores al cargar el archivo de datos durante el inicio.
- Posibilidad de seleccionar una copia para recuperar la información o salir sin reemplazar automáticamente el archivo dañado.

Las copias se crean cuando el usuario solicita la operación; actualmente no existe un sistema de respaldos automáticos.

Guardar una copia en la misma computadora no protege frente a la pérdida o avería del equipo. Para contar con una copia independiente, se puede seleccionar una unidad externa como destino.

## Tecnologías

| Tecnología | Utilización |
|---|---|
| Python | Lenguaje principal |
| CustomTkinter | Interfaz gráfica |
| Tkinter | Cuadros de diálogo y selección de archivos |
| JSON | Persistencia local |
| Decimal | Cálculos monetarios |
| UUID | Identificación de clientes |
| pytest | Pruebas automatizadas |
| GitHub Actions | Ejecución de pruebas en Windows |
| Ed25519 | Verificación de firmas digitales de licencias |

El proyecto utiliza también módulos de la biblioteca estándar de Python para la gestión de archivos, fechas y copias de seguridad.

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
│   ├── test_copias_seguridad.py
│   ├── test_dinero.py
│   ├── test_fechas.py
│   ├── test_guardado_seguro.py
│   ├── test_inventario.py
│   ├── test_licencias.py
│   ├── test_pedidos.py
│   ├── test_persistencia.py
│   ├── test_recuperacion_inicio.py
│   └── test_restauracion.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── README.md
├── .gitignore
└── .gitattributes
```

### Organización del código

- `app_grafica.py`: interfaz gráfica, activación e inicio de la aplicación.
- `modelos.py`: clases `Cliente`, `Pedido` y `PartePedido`, junto con sus cálculos y representación como diccionarios.
- `sistema.py`: gestión de datos, persistencia, reportes, copias de seguridad y restauración.
- `validaciones.py`: validaciones reutilizables.
- `licencias.py`: identificación del equipo y verificación de licencias firmadas.
- `tests/`: pruebas automatizadas de la lógica del programa.
- `.github/workflows/tests.yml`: configuración de las pruebas ejecutadas mediante GitHub Actions.

## Cómo funciona el programa

La aplicación separa la interfaz, los modelos de datos y las operaciones de persistencia.

### Ejemplo: registrar un cliente

1. El usuario introduce los datos en la interfaz gráfica.
2. `app_grafica.py` crea un objeto `Cliente`.
3. El objeto se incorpora a la lista de clientes de `SistemaInvernadero`.
4. `guardar_datos()` convierte los objetos en diccionarios compatibles con JSON.
5. El sistema escribe el contenido en un archivo temporal y, cuando termina correctamente, reemplaza el archivo de datos.

De esta manera, el archivo JSON no se sobrescribe directamente mientras se está escribiendo la nueva información.

### Ejemplo: iniciar la aplicación

1. Se comprueba la licencia de la instalación.
2. El sistema intenta cargar `datos_invernadero.json`.
3. Se reconstruyen los objetos `Cliente`, `Pedido` y `PartePedido` a partir de los datos guardados.
4. Si la carga finaliza correctamente, se abre la ventana principal.
5. Si la carga falla, el programa ofrece seleccionar una copia de seguridad o salir sin reemplazar automáticamente los datos existentes.

Cuando el archivo todavía no existe, el sistema puede comenzar con una lista vacía de clientes. Esto es distinto de encontrar un archivo existente cuyo contenido es inválido.

### Ejemplo: restaurar una copia

Antes de reemplazar el archivo actual, el programa comprueba que la copia seleccionada tiene una estructura válida y que sus datos pueden cargarse. Si existe un archivo anterior, intenta conservarlo como respaldo y después realiza el reemplazo.

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

La aplicación requiere una licencia válida para acceder a sus funcionalidades. El generador de licencias y la clave privada no forman parte del repositorio.

## Pruebas automatizadas

El proyecto cuenta actualmente con **29 pruebas automatizadas** desarrolladas con `pytest`.

Para ejecutarlas:

```bash
python -m pytest -v
```

Las pruebas abarcan:

- Cálculos de pedidos, pagos y saldos.
- Persistencia de datos.
- Identificadores únicos y clientes con nombres repetidos.
- Inventario activo.
- Validación de fechas.
- Conservación de importes decimales.
- Manejo de errores durante el guardado.
- Verificación de licencias firmadas.
- Creación y validación de copias de seguridad.
- Restauración y conservación del archivo anterior.
- Recuperación de datos después de simular un archivo dañado.

Las pruebas que trabajan con archivos utilizan directorios temporales para evitar modificar los datos locales del usuario.

GitHub Actions ejecuta las pruebas en Windows cuando se realizan cambios o se abren pull requests hacia `main`.

**Alcance de las pruebas:** los 29 casos automatizados verifican principalmente la lógica y la persistencia. Los flujos de la interfaz gráfica, incluidos los diálogos de copias y recuperación, también se han comprobado manualmente, pero todavía no cuentan con pruebas automatizadas de interfaz.

## Persistencia

La aplicación almacena la información en:

```text
datos_invernadero.json
```

El archivo contiene los clientes, sus pedidos y sus abonos.

Los importes monetarios se guardan como cadenas decimales y se recuperan como objetos `Decimal`.

### Guardado seguro

El sistema utiliza archivos temporales y `os.replace()` para evitar sobrescribir directamente el JSON original durante la escritura.

Si ocurre un error antes de completar el reemplazo, se busca conservar el archivo anterior. Este mecanismo reduce riesgos durante el guardado, pero no sustituye las copias de seguridad.

Actualmente, la ubicación del archivo de datos depende de una ruta relativa. Definir una ubicación estable para futuras versiones ejecutables es una mejora pendiente.

El archivo de datos, las copias locales y la licencia están excluidos del repositorio mediante `.gitignore`.

## Activación

La aplicación dispone de un mecanismo de activación local asociado al identificador del equipo.

Las licencias utilizan firmas digitales Ed25519: el programa incluye una clave pública para verificarlas, mientras que la clave privada y el generador se mantienen fuera del repositorio y del programa distribuido.

Este mecanismo sirve para estudiar la firma y verificación de licencias, pero no debe considerarse una protección resistente frente a la ingeniería inversa.

## Estado y alcance

El proyecto se encuentra en desarrollo y se utiliza actualmente como experiencia práctica y proyecto de portafolio.

En su estado actual:

- Es una aplicación de escritorio.
- Funciona localmente.
- No requiere Internet para gestionar los datos.
- Utiliza JSON como almacenamiento.
- No dispone de sincronización entre equipos.
- No incluye una interfaz web.
- No se ha desplegado todavía para uso operativo en el invernadero.

La aplicación se ha desarrollado y probado en Windows con Python 3.14.

## Próximas mejoras

- Definir una ubicación estable para los archivos de datos al distribuir la aplicación.
- Preparar y comprobar una versión ejecutable para Windows.
- Ampliar las validaciones y las pruebas automatizadas, especialmente de la interfaz.
- Revisar la experiencia de uso y los mensajes de error.
- Continuar mejorando la documentación técnica.

La incorporación de otras tecnologías, como SQLite, se evaluará si aparecen necesidades concretas que lo justifiquen.

## Origen y objetivo del proyecto

Este proyecto nació a partir de una necesidad planteada por un familiar que administra un invernadero y buscaba una alternativa a los registros manuales.

Además de explorar una solución para ese problema, su objetivo es adquirir experiencia práctica en programación orientada a objetos, diseño de software, persistencia, interfaces gráficas, pruebas automatizadas, manejo de errores y control de versiones.

El desarrollo también busca comprender el funcionamiento completo de una aplicación: desde la entrada de datos hasta su almacenamiento, recuperación y distribución.