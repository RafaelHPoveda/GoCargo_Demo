# GoCargo Demo

GoCargo Demo es un backend de log?stica que permite administrar sucursales y registrar env?os internacionales. Valida el peso de los paquetes, la capacidad y el estado de la sucursal de origen, y consulta un cat?logo GraphQL para obtener informaci?n del pa?s de destino.

El proyecto utiliza **Django, Django REST Framework y SQLite**, con servicios e interfaces por m?dulo, repositorios separados y documentaci?n interactiva mediante **Scalar y OpenAPI**.

## Funcionalidades

- Crear, listar y actualizar sucursales mediante PUT o PATCH.
- Crear env?os y consultarlos en una lista o por UUID.
- Validar peso, capacidad de origen y disponibilidad del destino.
- Conservar los nombres y la informaci?n de moneda registrados al crear cada env?o.
- Explorar y probar las siete operaciones de negocio desde el navegador.

## Documentaci?n

| Documento | Contenido |
| --- | --- |
| [Arquitectura](.docs/arquitechture.md) | Organizaci?n, capas, contratos, integraci?n y decisiones de dise?o. |
| [Manual general](.docs/manual.md) | Instalaci?n, configuraci?n, uso de la API y resoluci?n de problemas frecuentes. |
| [Manual detallado](.docs/manual_detallado.md) | Archivos, clases, reglas, procesos internos, almacenamiento y pruebas. |

## Inicio r?pido

Ejecuta los comandos desde `GoCargo_Demo/`, en PowerShell. Necesitas Python compatible con las versiones fijadas en [requirements.txt](requirements.txt). Los manuales indican el entorno utilizado para validar la implementaci?n.

1. Para una instalaci?n nueva, crea el entorno e instala las dependencias. Si `env/` ya existe, reutil?zalo.

   ```powershell
   py -m venv env
   .\env\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Desde el editor, crea `.env` junto a `manage.py` utilizando [.env.example](.env.example) como plantilla. Genera una clave propia y gu?rdala en `DJANGO_SECRET_KEY`:

   ```powershell
   .\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

3. Prepara la base de datos e inicia el servidor:

   ```powershell
   .\env\Scripts\python.exe manage.py migrate
   .\env\Scripts\python.exe manage.py check
   .\env\Scripts\python.exe manage.py runserver
   ```

4. Abre [Scalar](http://127.0.0.1:8000/api/docs/), crea una sucursal y utiliza su UUID para registrar un env?o.

SQLite utiliza un archivo local y no requiere un servidor independiente. Las variables externas tienen prioridad sobre `.env`; reinicia el servidor despu?s de cambiar su configuraci?n. No publiques tu archivo `.env`.

## Acceso a la API

- **Documentaci?n interactiva:** [`/api/docs/`](http://127.0.0.1:8000/api/docs/).
- **Contrato OpenAPI:** [`/api/schema/`](http://127.0.0.1:8000/api/schema/).
- **Recursos de negocio:** `/api/branches/` y `/api/shipments/`.

El [manual general](.docs/manual.md#5-operaciones-http) describe todas las rutas y los ejemplos de uso. Los listados devuelven listas JSON sin paginaci?n. Leer env?os utiliza datos locales; crear uno necesita acceso al cat?logo externo.

Scalar carga su interfaz desde un CDN y necesita internet en el navegador. El esquema JSON est? disponible localmente y se mantiene en `config/openapi.json`.

## Organizaci?n

```text
apps/         M?dulos de sucursales y env?os
core/         Contratos y persistencia compartidos
config/       Configuraci?n, dependencias, rutas y OpenAPI
templates/    P?gina de documentaci?n Scalar
.docs/        Arquitectura y manuales
```

Los servicios coordinan las acciones y el dominio protege las reglas. Los adaptadores concentran ORM e integraciones; los contratos permiten evolucionar esas dependencias sin trasladarlas al n?cleo.

## Pruebas

```powershell
.\env\Scripts\python.exe manage.py test
```

La suite actual contiene **64 pruebas** de dominio, servicios, persistencia, transacciones, integraci?n, API y documentaci?n. Sustituye el cat?logo remoto y no requiere internet.

## Alcance

Esta demo ofrece acceso an?nimo a la API de negocio. No incluye frontend de log?stica, eliminaci?n, edici?n de env?os, tarifas ni seguimiento. PostgreSQL y SQL Server son alternativas futuras pendientes de validaci?n. Los manuales detallan las limitaciones de concurrencia y la configuraci?n adicional necesaria para desplegar.
