# GoCargo Demo

GoCargo Demo es un backend de logística que permite administrar sucursales y registrar envíos internacionales. Valida el peso de los paquetes, la capacidad y el estado de la sucursal de origen, y consulta un catálogo GraphQL para obtener información del país de destino.

El proyecto utiliza **Django, Django REST Framework y SQLite**, con servicios e interfaces por módulo, repositorios separados y documentación interactiva mediante **Scalar y OpenAPI**.

## Funcionalidades

- Crear, listar y actualizar sucursales mediante PUT o PATCH.
- Crear envíos y consultarlos en una lista o por UUID.
- Validar peso, capacidad de origen y disponibilidad del destino.
- Conservar los nombres y la información de moneda registrados al crear cada envío.
- Explorar y probar las siete operaciones de negocio desde el navegador.

## Documentación

| Documento | Contenido |
| --- | --- |
| [Arquitectura](.docs/arquitechture.md) | Organización, capas, contratos, integración y decisiones de diseño. |
| [Manual general](.docs/manual.md) | Instalación, configuración, uso de la API y resolución de problemas frecuentes. |
| [Manual detallado](.docs/manual_detallado.md) | Archivos, clases, reglas, procesos internos, almacenamiento y pruebas. |

## Inicio rápido

Ejecuta los comandos desde `GoCargo_Demo/`, en PowerShell. Necesitas Python compatible con las versiones fijadas en [requirements.txt](requirements.txt). Los manuales indican el entorno utilizado para validar la implementación.

1. Para una instalación nueva, crea el entorno e instala las dependencias. Si `env/` ya existe, reutilízalo.

   ```powershell
   py -m venv env
   .\env\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Desde el editor, crea `.env` junto a `manage.py` utilizando [.env.example](.env.example) como plantilla. Genera una clave propia y guárdala en `DJANGO_SECRET_KEY`:

   ```powershell
   .\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

3. Prepara la base de datos e inicia el servidor:

   ```powershell
   .\env\Scripts\python.exe manage.py migrate
   .\env\Scripts\python.exe manage.py check
   .\env\Scripts\python.exe manage.py runserver
   ```

4. Abre [Scalar](http://127.0.0.1:8000/api/docs/), crea una sucursal y utiliza su UUID para registrar un envío.

SQLite utiliza un archivo local y no requiere un servidor independiente. Las variables externas tienen prioridad sobre `.env`; reinicia el servidor después de cambiar su configuración. No publiques tu archivo `.env`.

## Acceso a la API

- **Documentación interactiva:** [`/api/docs/`](http://127.0.0.1:8000/api/docs/).
- **Contrato OpenAPI:** [`/api/schema/`](http://127.0.0.1:8000/api/schema/).
- **Recursos de negocio:** `/api/branches/` y `/api/shipments/`.

El [manual general](.docs/manual.md#5-operaciones-http) describe todas las rutas y los ejemplos de uso. Los listados devuelven listas JSON sin paginación. Leer envíos utiliza datos locales; crear uno necesita acceso al catálogo externo.

Scalar carga su interfaz desde un CDN y necesita internet en el navegador. El esquema JSON está disponible localmente y se mantiene en `config/openapi.json`.

## Organización

```text
apps/         Módulos de sucursales y envíos
core/         Contratos y persistencia compartidos
config/       Configuración, dependencias, rutas y OpenAPI
templates/    Página de documentación Scalar
.docs/        Arquitectura y manuales
```

Los servicios coordinan las acciones y el dominio protege las reglas. Los adaptadores concentran ORM e integraciones; los contratos permiten evolucionar esas dependencias sin trasladarlas al núcleo.

## Pruebas

```powershell
.\env\Scripts\python.exe manage.py test
```

La suite actual contiene **64 pruebas** de dominio, servicios, persistencia, transacciones, integración, API y documentación. Sustituye el catálogo remoto y no requiere internet.

## Alcance

Esta demo ofrece acceso anónimo a la API de negocio. No incluye frontend de logística, eliminación, edición de envíos, tarifas ni seguimiento. PostgreSQL y SQL Server son alternativas futuras pendientes de validación. Los manuales detallan las limitaciones de concurrencia y la configuración adicional necesaria para desplegar.
