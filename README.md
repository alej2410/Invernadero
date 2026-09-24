# 🌱 Sistema de Gestión para Invernadero

Aplicación de escritorio desarrollada en Python para gestionar clientes, pedidos, siembras, entregas, pagos e inventario de un invernadero.

El proyecto surge de una necesidad planteada por un familiar: sustituir los registros en cuadernos por un sistema que facilite organizar y consultar la información.

Actualmente se desarrolla como proyecto de aprendizaje y portafolio. La aplicación es funcional y cuenta con una versión empaquetada para Windows, aunque todavía no se ha desplegado para uso operativo en el invernadero.

Funciona de manera local, con una interfaz gráfica desarrollada en CustomTkinter y almacenamiento en JSON.

## Funcionalidades

### Gestión de clientes

- Registro de clientes con nombre, teléfono, cédula y ubicación.
- Búsqueda parcial por nombre.
- Edición de información.
- Identificadores únicos mediante UUID.
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

- Creación manual de copias de seguridad desde la interfaz gráfica.
- Selección de la carpeta donde se guardará cada copia.
- Validación del archivo antes de crear una copia.
- Restauración mediante selector de archivos y confirmación.
- Validación de la copia antes de reemplazar los datos actuales.
- Conservación del archivo reemplazado antes de completar una restauración.
- Detección de errores al cargar los datos durante el inicio.
- Recuperación desde una copia de seguridad cuando el archivo principal no puede cargarse.
- Posibilidad de salir sin modificar automáticamente un archivo dañado.

Las copias se crean cuando el usuario solicita la operación; actualmente no existe un sistema de respaldos automáticos.

Guardar una copia únicamente en la misma computadora no protege frente a la pérdida o avería del equipo. El sistema permite seleccionar una ubicación externa para guardar respaldos independientes.

## Tecnologías

| Tecnología | Utilización |
|---|---|
| Python | Lenguaje principal |
| CustomTkinter | Interfaz gráfica |
| Tkinter | Cuadros de diálogo y selección de archivos |
| JSON | Persistencia local |
| Decimal | Cálculos monetarios |
| UUID | Identificación de clientes |
| pathlib | Gestión de rutas y archivos |
| pytest | Pruebas automatizadas |
| GitHub Actions | Integración continua y ejecución de pruebas en Windows |
| Ed25519 | Firma y verificación de licencias |
| PyInstaller | Empaquetado de la aplicación para Windows |

El proyecto utiliza también distintos módulos de la biblioteca estándar de Python para trabajar con archivos, fechas, copias de seguridad y operaciones seguras de escritura.

## Estructura del proyecto

```text
Invernadero/
│
├── app_grafica.py
├── modelos.py
├── sistema.py
├── validaciones.py
├── licencias.py
├── rutas.py
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
│   ├── test_restauracion.py
│   └── test_rutas.py
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

- `app_grafica.py`: interfaz gráfica, activación, interacción con el usuario e inicio de la aplicación.
- `modelos.py`: clases `Cliente`, `Pedido` y `PartePedido`, junto con sus cálculos y conversión a estructuras compatibles con JSON.
- `sistema.py`: gestión de datos, persistencia, reportes, copias de seguridad y restauración.
- `validaciones.py`: validaciones reutilizables.
- `licencias.py`: identificación del equipo y verificación criptográfica de licencias.
- `rutas.py`: definición de las ubicaciones estables utilizadas para los datos y la licencia.
- `tests/`: pruebas automatizadas de la lógica, persistencia y manejo de archivos.
- `.github/workflows/tests.yml`: configuración de las pruebas ejecutadas mediante GitHub Actions.

## Cómo funciona el programa

La aplicación separa la interfaz gráfica, los modelos de datos, la persistencia y otras responsabilidades auxiliares.

### Ejemplo: registrar un cliente

1. El usuario introduce los datos en la interfaz gráfica.
2. `app_grafica.py` crea un objeto `Cliente`.
3. El objeto se incorpora a la lista de clientes de `SistemaInvernadero`.
4. `guardar_datos()` convierte los objetos en diccionarios compatibles con JSON.
5. El sistema escribe primero el contenido en un archivo temporal.
6. Cuando la escritura termina correctamente, `os.replace()` sustituye el archivo de datos anterior.

De esta manera, el JSON principal no se sobrescribe directamente durante el proceso de escritura.

### Ejemplo: iniciar la aplicación

1. Se determina la ruta de la licencia.
2. Se comprueba la licencia de la instalación.
3. Se determina la ruta estable del archivo de datos.
4. El sistema intenta cargar `datos_invernadero.json`.
5. Se reconstruyen los objetos `Cliente`, `Pedido` y `PartePedido`.
6. Si la carga finaliza correctamente, se abre la ventana principal.
7. Si la carga falla, el programa ofrece recuperar una copia de seguridad o salir sin reemplazar automáticamente los datos existentes.

Cuando el archivo todavía no existe, el sistema puede comenzar con una lista vacía de clientes. Esto es distinto de encontrar un archivo existente cuyo contenido sea inválido.

### Ejemplo: restaurar una copia

Antes de reemplazar el archivo actual, el programa comprueba que la copia seleccionada tenga una estructura válida y que pueda cargarse correctamente.

Si existe un archivo anterior, el programa intenta conservarlo como respaldo antes de completar el reemplazo.

Después de restaurar, el sistema vuelve a comprobar que los datos puedan cargarse correctamente.

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

En Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install customtkinter pytest cryptography pyinstaller
```

### 4. Ejecutar la aplicación

```bash
python app_grafica.py
```

La aplicación requiere una licencia válida para acceder a sus funcionalidades.

El generador de licencias y la clave privada utilizada para firmarlas no forman parte del repositorio.

## Pruebas automatizadas

El proyecto cuenta actualmente con **33 pruebas automatizadas** desarrolladas con `pytest`.

Para ejecutarlas:

```bash
python -m pytest -v
```

Las pruebas abarcan:

- Cálculos de pedidos.
- Cálculo de pagos y saldos.
- Registro de abonos.
- Persistencia de datos.
- Identificadores únicos.
- Clientes con nombres repetidos.
- Inventario activo.
- Validación de fechas.
- Conservación exacta de importes decimales.
- Manejo de errores durante el guardado.
- Escritura segura mediante archivos temporales.
- Verificación de licencias firmadas.
- Creación y validación de copias de seguridad.
- Restauración de datos.
- Conservación del archivo reemplazado.
- Recuperación después de simular un archivo dañado.
- Uso de una ubicación estable para los archivos de aplicación.
- Creación automática de la carpeta de datos cuando todavía no existe.
- Ubicación común para los datos y la licencia.

Las pruebas que trabajan con archivos utilizan directorios temporales para evitar modificar los datos reales del usuario.

GitHub Actions ejecuta las pruebas automáticamente en Windows cuando se realizan determinados cambios o se abren pull requests hacia `main`.

### Alcance de las pruebas

Las 33 pruebas automatizadas verifican principalmente la lógica, persistencia y manejo de archivos.

Los flujos de la interfaz gráfica también se han comprobado manualmente, pero actualmente no cuentan con pruebas automatizadas de interfaz.

## Persistencia

La aplicación utiliza JSON como almacenamiento local.

El archivo principal es:

```text
datos_invernadero.json
```

Contiene los clientes, sus pedidos, partes de pedidos y abonos.

Los importes monetarios se guardan como cadenas decimales y se reconstruyen como objetos `Decimal` al cargarlos.

### Ubicación de los datos

En Windows, los archivos propios de la aplicación se almacenan dentro de:

```text
%LOCALAPPDATA%\Invernadero\
```

Actualmente se utilizan, entre otros:

```text
%LOCALAPPDATA%\Invernadero\datos_invernadero.json
%LOCALAPPDATA%\Invernadero\licencia.key
```

Esto permite que los datos y la licencia sean independientes de:

- La carpeta desde la que se ejecute el programa.
- La ubicación del ejecutable.
- El repositorio del código fuente.
- La carpeta utilizada durante la compilación.

La carpeta se crea automáticamente cuando es necesario guardar información.

### Guardado seguro

El sistema utiliza archivos temporales y `os.replace()` para evitar sobrescribir directamente el JSON original durante una escritura.

Si ocurre un error antes de completar el reemplazo, se busca conservar intacto el archivo anterior.

Este mecanismo reduce el riesgo de corrupción durante un guardado, pero no sustituye las copias de seguridad.

El archivo de datos, las copias locales y la licencia están excluidos del repositorio mediante `.gitignore`.

## Activación

La aplicación dispone de un mecanismo de activación local asociado a un identificador del equipo.

Las licencias utilizan firmas digitales Ed25519.

El programa incluye únicamente la clave pública necesaria para verificar una licencia.

La clave privada utilizada para generar firmas y el generador de licencias se mantienen fuera del repositorio y de la aplicación distribuida.

Este mecanismo constituye una implementación práctica de firma y verificación criptográfica, pero no debe considerarse una protección resistente frente a ingeniería inversa.

## Distribución

La aplicación puede empaquetarse para Windows mediante PyInstaller.

La compilación candidata a **v1.0.0** se ha generado como aplicación de 64 bits para Windows y ha sido probada después de copiarse y extraerse en ubicaciones independientes del repositorio y del entorno de desarrollo.

El ejecutable utiliza los archivos almacenados en `%LOCALAPPDATA%\Invernadero`, por lo que los datos del usuario no dependen de la carpeta donde se encuentre el programa.

### Flujos comprobados desde la aplicación empaquetada

Se han probado manualmente:

- Inicio de la aplicación desde el ejecutable.
- Activación mediante licencia.
- Conservación de la licencia después de cerrar y volver a abrir.
- Creación de clientes.
- Persistencia después de cerrar la aplicación.
- Creación de pedidos.
- Registro de abonos.
- Recuperación de clientes, pedidos y pagos después de reiniciar.
- Creación de copias de seguridad.
- Restauración de una copia existente.
- Ejecución de la aplicación después de extraer el paquete en una ubicación diferente.

La ejecución en una segunda computadora física todavía no ha sido validada.

## Estado y alcance

El proyecto se encuentra en una etapa funcional y se utiliza principalmente como experiencia práctica y proyecto de portafolio.

Actualmente:

- Es una aplicación de escritorio.
- Funciona localmente.
- No requiere Internet para gestionar los datos.
- Utiliza JSON como almacenamiento.
- Cuenta con guardado seguro.
- Cuenta con copias de seguridad y restauración.
- Puede recuperarse ante determinados errores del archivo de datos.
- Utiliza licencias firmadas digitalmente.
- Cuenta con pruebas automatizadas e integración continua.
- Puede empaquetarse como aplicación ejecutable para Windows.
- Utiliza una ubicación estable para los archivos de usuario.
- No dispone de sincronización entre equipos.
- No incluye una interfaz web.
- Todavía no ha sido desplegada para uso operativo real en el invernadero.

La aplicación se ha desarrollado y probado principalmente en Windows con Python 3.14.

## Próximas mejoras

El objetivo actual no es añadir funcionalidades sin una necesidad concreta, sino mantener una versión estable y mejorarla cuando existan motivos reales para hacerlo.

Posibles mejoras futuras:

- Probar la distribución en otras computadoras Windows.
- Automatizar parcialmente las pruebas de la interfaz gráfica.
- Mejorar algunos aspectos de experiencia de usuario.
- Refinar los mensajes de error.
- Incorporar un instalador si la distribución del programa lo requiere.
- Evaluar copias de seguridad automáticas si un usuario real las necesita.
- Incorporar nuevas funcionalidades según el uso real del sistema.

Tecnologías adicionales, como SQLite, se evaluarán únicamente si aparecen requisitos que justifiquen el cambio.

## Origen y objetivo del proyecto

Este proyecto nació a partir de una necesidad planteada por un familiar que administra un invernadero y buscaba una alternativa a los registros manuales de clientes y pedidos.

Además de explorar una solución para ese problema, el proyecto tiene como objetivo adquirir experiencia práctica en:

- Programación orientada a objetos.
- Diseño y organización de software.
- Persistencia de datos.
- Manejo de información monetaria.
- Interfaces gráficas.
- Manejo seguro de archivos.
- Copias de seguridad y recuperación.
- Criptografía aplicada a licencias.
- Pruebas automatizadas.
- Integración continua.
- Control de versiones con Git y GitHub.
- Empaquetado y distribución de aplicaciones de escritorio.

El desarrollo busca comprender el funcionamiento completo de una aplicación: desde la entrada de datos y su representación mediante objetos hasta su almacenamiento, recuperación, protección, prueba y distribución.