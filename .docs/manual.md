# Manual general de GoCargo Demo

## 1. Qué es GoCargo Demo

GoCargo Demo es una API de logística para registrar sucursales y envíos internacionales. Permite conocer desde qué sucursal sale un paquete, validar su peso y guardar el destino con información de un catálogo público de países.

El backend utiliza Django, Django REST Framework y SQLite. La documentación interactiva se presenta con Scalar. Es una demostración local de organización del código y comportamiento de negocio; no incluye una aplicación web para usuarios finales.

Este manual explica cómo preparar y utilizar el sistema. La [arquitectura](arquitechture.md) describe su diseño; el [manual detallado](manual_detallado.md) explica sus archivos, reglas y procesos internos.

## 2. Funcionalidades disponibles

| Área | Funcionalidades |
| --- | --- |
| Sucursales | Crear, listar, actualizar todos sus campos editables o modificar solo algunos. |
| Envíos | Crear, listar y consultar un registro por UUID. |
| Validación | Revisar peso, capacidad de sucursal, estado activo y existencia del país. |
| Documentación | Consultar ejemplos y ejecutar solicitudes desde Scalar; descargar OpenAPI JSON. |

Los envíos guardan nombres históricos de sucursal y país, además de la información de moneda. Cambiar posteriormente una sucursal no altera esos valores ya registrados.

## 3. Preparar el entorno

Todos los comandos siguientes se ejecutan desde `GoCargo_Demo/` en PowerShell. La implementación fue revisada con Python 3.15.2 y Django 6.1.2; las dependencias exactas están en [requirements.txt](../requirements.txt).

Si ya tienes el entorno `env/`, utilízalo. Para una instalación nueva:

```powershell
py -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
```

Desde el editor, crea `.env` junto a `manage.py` utilizando `.env.example` como plantilla. Genera una clave local con:

```powershell
.\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia la cadena generada al valor de `DJANGO_SECRET_KEY` dentro de `.env`. No publiques ese archivo ni copies la clave a la plantilla compartida.

Variables principales:

| Variable | Uso |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave interna de Django. Debe tener un valor propio. |
| `DJANGO_DEBUG` | `True` para desarrollo local; `False` fuera de ese contexto. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, por ejemplo `127.0.0.1,localhost`. |
| `DJANGO_TIME_ZONE` | Zona horaria, normalmente `America/Managua`. |
| `SQLITE_NAME` | Nombre de archivo local, normalmente `db.sqlite3`. |
| `COUNTRIES_API_URL` | Dirección del catálogo GraphQL de países. |
| `COUNTRIES_CONNECT_TIMEOUT` | Tiempo de espera de conexión, en segundos. |
| `COUNTRIES_READ_TIMEOUT` | Tiempo de espera de lectura, en segundos. |

El archivo se carga automáticamente al iniciar Django. Las variables ya existentes en el entorno tienen prioridad. Guarda y reinicia el servidor después de modificar `.env`.

## 4. Iniciar el proyecto

```powershell
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py check
.\env\Scripts\python.exe manage.py runserver
```

`migrate` prepara las tablas; `check` revisa la configuración; `runserver` inicia el servidor local. SQLite no requiere un servicio de base de datos independiente. Pulsa `Ctrl+C` en la terminal para detener el servidor.

Abre [Scalar](http://127.0.0.1:8000/api/docs/) para trabajar con la API. El [esquema JSON](http://127.0.0.1:8000/api/schema/) contiene el contrato de sus operaciones. Scalar necesita internet en el navegador para cargar su interfaz desde el CDN; el JSON se sirve localmente.

La dirección `/` no tiene una página configurada y puede devolver `404`. Eso no indica que las rutas de API estén fallando.

## 5. Operaciones HTTP

| Método | Ruta | Acción |
| --- | --- | --- |
| GET | `/api/branches/` | Listar sucursales. |
| POST | `/api/branches/` | Crear una sucursal. |
| PUT | `/api/branches/{id}/` | Actualizar sus cuatro campos editables. |
| PATCH | `/api/branches/{id}/` | Actualizar únicamente campos enviados. |
| GET | `/api/shipments/` | Listar envíos. |
| POST | `/api/shipments/` | Crear un envío internacional. |
| GET | `/api/shipments/{id}/` | Consultar un envío específico. |

Sustituye `{id}` por un UUID real. Los listados devuelven listas JSON sin paginación; las sucursales se ordenan por nombre y UUID, y los envíos por UUID. El orden de envíos no representa necesariamente su fecha de creación.

## 6. Primer recorrido

Mantén el servidor en una terminal y abre otra para las solicitudes. También puedes realizar este recorrido desde Scalar copiando los mismos cuerpos JSON.

### 6.1. Crear una sucursal

```powershell
$baseUrl = 'http://127.0.0.1:8000'
$body = @{
    name = 'Sucursal Managua'
    city = 'Managua'
    max_weight_kg = '25.00'
    is_active = $true
} | ConvertTo-Json
$branch = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/branches/" -ContentType application/json -Body $body
$branch
```

La respuesta `201` contiene un UUID generado por el servidor. Conserva `$branch.id`. La capacidad debe ser positiva y tener hasta dos decimales. La sucursal necesita estar activa para admitir envíos nuevos.

### 6.2. Crear un envío

```powershell
$body = @{
    origin_branch_id = $branch.id
    description = 'Documentos de demostración'
    weight_kg = '2.50'
    destination_country_code = 'CR'
} | ConvertTo-Json
$shipment = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/shipments/" -ContentType application/json -Body $body
$shipment
```

El peso debe ser mayor que cero, no superar 50 kg y respetar la capacidad de la sucursal. El servidor consulta el país y guarda el envío con estado `CREATED`. Si el catálogo no está disponible, responde `503` y no crea el registro.

### 6.3. Consultar los datos

```powershell
Invoke-RestMethod -Uri "$baseUrl/api/branches/"
Invoke-RestMethod -Uri "$baseUrl/api/shipments/"
Invoke-RestMethod -Uri "$baseUrl/api/shipments/$($shipment.id)/"
```

Estas consultas usan la base local. Leer un envío no vuelve a consultar el país ni depende de que su sucursal siga activa.

### 6.4. Modificar una sucursal

```powershell
$changes = @{ city = 'Leon'; is_active = $false } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "$baseUrl/api/branches/$($branch.id)/" -ContentType application/json -Body $changes
```

`PATCH` conserva los campos omitidos. Para `PUT` debes enviar `name`, `city`, `max_weight_kg` e `is_active`. No se acepta un cuerpo vacío, valores nulos ni campos desconocidos en actualización.

Inactivar la sucursal impide crear envíos nuevos desde ella. Los envíos anteriores siguen disponibles y conservan su nombre histórico. Para reactivarla, envía otro `PATCH` con `is_active = $true`.

## 7. Interpretar las respuestas

| Estado | Significado |
| --- | --- |
| `200` | Consulta o actualización correcta. |
| `201` | Registro creado. |
| `400` | Formato, campos o cuerpo inválidos. |
| `404` | Recurso o referencia inexistente. |
| `409` | Conflicto al guardar datos. |
| `422` | Regla incumplida: peso, capacidad o estado. |
| `503` | Catálogo o persistencia no disponibles. |

Un error esperado suele tener esta forma:

```json
{
  "code": "branch_inactive",
  "detail": "La sucursal está inactiva."
}
```

Los errores de formato pueden agregar `errors` con detalle por campo. En PowerShell, `Invoke-RestMethod` lanza una excepción ante estados de error; revisa su cuerpo o usa Scalar para ver la respuesta.

## 8. Ejecutar las pruebas

```powershell
.\env\Scripts\python.exe manage.py test
```

La suite actual tiene 64 pruebas de negocio, servicios, persistencia, integración, API y documentación. Sustituye las llamadas externas y no requiere internet. Django crea una base de pruebas separada de la base local de desarrollo.

## 9. Resolver problemas frecuentes

| Problema | Revisión sugerida |
| --- | --- |
| Falta la clave de Django | Confirma `.env` junto a `manage.py` y un valor propio en `DJANGO_SECRET_KEY`. |
| No se encuentra un paquete | Usa el ejecutable de `env/` e instala `requirements.txt` en ese entorno. |
| `DisallowedHost` | Revisa hosts separados por comas, sin esquema ni puerto. |
| Faltan tablas | Ejecuta `manage.py migrate`. |
| Scalar no carga | Revisa acceso a jsDelivr; abre `/api/schema/` para verificar el contrato local. |
| Crear un envío devuelve `503` | Revisa conexión, endpoint y respuesta del proveedor. |
| Una ruta devuelve `404` | Verifica su escritura, barra final y UUID; la raíz no tiene página propia. |

## 10. Límites de la demo

La API de negocio es anónima. No incluye eliminación, edición de envíos, autenticación JWT, cálculo de tarifas, seguimiento, frontend ni colas de procesamiento.

SQLite es el motor implementado. PostgreSQL y SQL Server son alternativas de evolución, pendientes de comprobar con sus dependencias y características. El catálogo externo real no pudo verificarse desde el entorno donde se completó el proyecto; las pruebas de integración utilizan respuestas simuladas.
