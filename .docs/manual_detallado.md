# Manual detallado de GoCargo Demo

## Índice

1. [Alcance y conceptos](#1-alcance-y-conceptos).
2. [Tecnologías y preparación](#2-tecnologías-y-preparación).
3. [Configuración y variables de entorno](#3-configuración-y-variables-de-entorno).
4. [Carpetas y archivos de arranque](#4-carpetas-y-archivos-de-arranque).
5. [Recorrido de una solicitud](#5-recorrido-de-una-solicitud).
6. [Contratos y persistencia compartida](#6-contratos-y-persistencia-compartida).
7. [Módulo de sucursales](#7-módulo-de-sucursales).
8. [Módulo de envíos](#8-módulo-de-envíos).
9. [Comunicación entre módulos](#9-comunicación-entre-módulos).
10. [Catálogo GraphQL](#10-catálogo-graphql).
11. [Tablas, modelos y migraciones](#11-tablas-modelos-y-migraciones).
12. [Transacciones y concurrencia](#12-transacciones-y-concurrencia).
13. [Contrato HTTP y ejemplos](#13-contrato-http-y-ejemplos).
14. [Errores y respuestas](#14-errores-y-respuestas).
15. [Documentación OpenAPI y Scalar](#15-documentación-openapi-y-scalar).
16. [Pruebas](#16-pruebas).
17. [Diagnóstico y mantenimiento](#17-diagnóstico-y-mantenimiento).
18. [Límites y evolución](#18-límites-y-evolución).

## 1. Alcance y conceptos

Este manual describe el código implementado en `GoCargo_Demo/`, incluyendo sus reglas, configuración, contratos, almacenamiento, API y pruebas. Las rutas de archivos en tablas son relativas a esa carpeta. No se describen funcionalidades futuras como si ya existieran.

El [manual general](manual.md) permite instalar y recorrer la demo; el documento de [arquitectura](arquitechture.md) explica sus decisiones estructurales.

### 1.1. Problema que resuelve

Una sucursal dispone de nombre, ciudad, capacidad por paquete y estado activo. Un envío sale de una sucursal, transporta un paquete con peso válido y tiene un país de destino consultado en un catálogo GraphQL.

Para registrar el envío, el backend debe comprobar que la sucursal exista y esté activa, que su capacidad admita el paquete y que el catálogo devuelva información válida del país. Solo entonces puede guardar el registro local.

### 1.2. Vocabulario utilizado

| Concepto | Significado en este proyecto |
| --- | --- |
| App Django | Paquete registrado en `INSTALLED_APPS`, como `apps.branches`. |
| Módulo de negocio | Conjunto de responsabilidades de sucursales o envíos. |
| Entidad | Objeto con identidad UUID y reglas propias, como `Branch`. |
| Objeto de valor | Dato inmutable validado, como `PackageWeight`. |
| DTO | Estructura tipada para transferir entradas o resultados de aplicación. |
| Interfaz de servicio | Acciones públicas que un módulo ofrece a sus consumidores. |
| Puerto | Contrato de salida que aplicación necesita para persistir o consultar otros sistemas. |
| Adaptador | Implementación concreta de un puerto, por ejemplo un repositorio Django. |
| Mapper | Conversión entre representaciones propias y externas o de almacenamiento. |
| Unidad de trabajo | Contexto que delimita una transacción local. |
| Serializer | Validación y representación de datos en la frontera HTTP. |
| Instantánea histórica | Valor guardado al crear un envío, independiente de cambios posteriores en su origen. |

### 1.3. Por qué servicios con interfaces

El sistema agrupa acciones en `BranchService` y `ShipmentService`, con los contratos `IBranchService` e `IShipmentService`. Cada método implementa un caso de uso, pero no se crea una clase adicional por operación.

Las interfaces se expresan con `typing.Protocol`. Su utilidad es describir las firmas que deben ofrecer los colaboradores; no generan métodos, consultas ni validación de datos. Las anotaciones de tipos tampoco comprueban automáticamente los valores recibidos en ejecución.

Los servicios heredan explícitamente sus interfaces para mostrar la intención de implementarlas. También es posible cumplir un `Protocol` estructuralmente. El proyecto no usa `isinstance` para comprobar estos contratos ni necesita `runtime_checkable`.

## 2. Tecnologías y preparación

### 2.1. Componentes instalados

| Componente | Uso |
| --- | --- |
| Python | Lenguaje del dominio y del backend. El entorno revisado utiliza 3.15.2. |
| Django | Configuración, arranque, ORM, migraciones y servidor de desarrollo. |
| Django REST Framework | Vistas de API, serializers y respuestas HTTP. |
| SQLite | Persistencia inicial en un archivo local. |
| `requests` | Transporte HTTP síncrono para GraphQL. |
| `python-dotenv` | Carga de variables desde `.env`. |
| Scalar | Interfaz web para consultar y probar OpenAPI. |
| `unittest` y runner Django | Pruebas unitarias, de integración y HTTP. |

Las versiones Python de los paquetes están fijadas en [requirements.txt](../requirements.txt). Entre las dependencias directas del entorno se encuentran Django 6.1.2, DRF 3.18.3, `requests` 2.34.2 y `python-dotenv` 1.2.4. No hay una dependencia Python de Scalar ni un generador automático instalado para OpenAPI.

### 2.2. Instalar o reutilizar el entorno

Abre PowerShell en `GoCargo_Demo/`. Si `env/` ya existe, utiliza su ejecutable. Para una copia nueva, prepara el entorno e instala los requisitos:

```powershell
py -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe -m pip check
```

`py` debe seleccionar una versión de Python compatible con las dependencias del proyecto. No recrees el entorno existente por ejecutar nuevamente los pasos de instalación.

Se utiliza la ruta explícita al intérprete para evitar depender de la activación de PowerShell. Si lo activas por tu cuenta, `python` debe apuntar al mismo entorno. No instales paquetes en otro intérprete esperando que aparezcan en `env/`.

## 3. Configuración y variables de entorno

### 3.1. Ubicación de `.env`

El archivo privado va en `GoCargo_Demo/.env`, al mismo nivel que `manage.py`. Desde el editor puedes crear una copia de `.env.example`, renombrarla a `.env` y completar los valores.

Ejemplo sin una clave privada real:

```dotenv
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_TIME_ZONE=America/Managua
SQLITE_NAME=db.sqlite3
COUNTRIES_API_URL=https://countries.trevorblades.com/graphql
COUNTRIES_CONNECT_TIMEOUT=3
COUNTRIES_READ_TIMEOUT=5
```

Genera una clave propia con:

```powershell
.\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia solo el resultado al valor de `DJANGO_SECRET_KEY` y guarda. No uses la clave de otra persona ni la publiques en documentación, Git o capturas de pantalla.

### 3.2. Carga y prioridad

En [settings.py](../config/settings.py), `BASE_DIR` se obtiene a partir de la ubicación del archivo y apunta a la raíz del proyecto Django. `load_dotenv(BASE_DIR / '.env', override=False)` carga el archivo sin reemplazar variables ya presentes en el proceso.

Por tanto, una variable definida anteriormente en la terminal o en el sistema puede tener prioridad sobre `.env`. Si un cambio parece no aplicarse, revisa esa prioridad y reinicia `runserver` después de guardar.

### 3.3. Significado de cada variable

| Variable | Tratamiento y efecto |
| --- | --- |
| `DJANGO_SECRET_KEY` | Se lee como texto; la configuración exige una clave no vacía. Es independiente de la conexión SQLite. |
| `DJANGO_DEBUG` | El texto se normaliza y se compara con `true`; determina el modo de depuración. |
| `DJANGO_ALLOWED_HOSTS` | Texto separado por comas, convertido a lista de hosts sin entradas vacías. No debe contener `http://` ni puertos. |
| `DJANGO_TIME_ZONE` | Establece la zona de referencia de Django. `USE_TZ` permanece habilitado. |
| `SQLITE_NAME` | Se combina con `BASE_DIR` para construir la ruta de SQLite. |
| `COUNTRIES_API_URL` | Se inyecta en el cliente GraphQL; no se consulta desde el dominio. |
| `COUNTRIES_CONNECT_TIMEOUT` | Se convierte a `float`; se usa como espera de conexión. |
| `COUNTRIES_READ_TIMEOUT` | Se convierte a `float`; se usa como espera de lectura. |

La configuración rechaza timeout menores o iguales a cero. Utiliza números positivos normales, sin unidades de texto. La tupla de conexión/lectura no es un presupuesto total exacto para toda la operación HTTP.

### 3.4. Otras configuraciones relevantes

`INSTALLED_APPS` conserva las apps estándar de Django, DRF y los dos módulos de negocio. `DATABASES['default']` selecciona el backend SQLite. `TEMPLATES[0]['DIRS']` incluye `BASE_DIR / 'templates'` para encontrar la página de Scalar.

`REST_FRAMEWORK['EXCEPTION_HANDLER']` apunta al traductor de errores de envíos, que delega casos generales al handler de `config/`. No se ha configurado autenticación JWT, paginación automática ni una política global de reintentos.

`MIDDLEWARE` conserva los componentes estándar. Las vistas de negocio declaran acceso anónimo explícito; eso no significa que se haya eliminado globalmente CSRF ni que la administración Django carezca de login.

## 4. Carpetas y archivos de arranque

### 4.1. Archivos generales

| Ruta | Responsabilidad |
| --- | --- |
| `manage.py` | Selecciona `config.settings` y ejecuta comandos de Django. |
| `requirements.txt` | Registra las versiones instalables de paquetes Python. |
| `.env.example` | Plantilla pública de variables, sin clave real. |
| `.gitignore` | Excluye entorno, secretos, cachés y base de desarrollo. |
| `README.md` | Presentación general y acceso rápido a documentación. |
| `.docs/` | Arquitectura y manuales de este proyecto. |
| `env/` | Entorno virtual local; no es código de negocio. |
| `db.sqlite3` | Archivo de datos local por defecto; no debe versionarse. |

### 4.2. Configuración y composición

| Ruta | Responsabilidad |
| --- | --- |
| `config/settings.py` | Lee configuración y declara apps, base, plantillas y handlers. |
| `config/urls.py` | Conecta módulos, documentación y administración. |
| `config/dependencies.py` | Construye servicios e inyecta implementaciones concretas. |
| `config/api_exception_handler.py` | Traduce errores de sucursales, repositorios y DRF. |
| `config/api_docs.py` | Sirve HTML Scalar y el archivo JSON de OpenAPI. |
| `config/openapi.json` | Define manualmente el contrato público de las siete operaciones. |
| `config/asgi.py`, `config/wsgi.py` | Puntos de entrada para servidores compatibles con Django. |

No hay una configuración de despliegue productivo en estos manuales. La existencia de `asgi.py` no convierte automáticamente los servicios actuales en asíncronos.

### 4.3. Paquetes de las apps

Cada app conserva `apps.py` para su `AppConfig`, `migrations/` para evolución del esquema y `models/__init__.py` para descubrimiento ORM.

Los `__init__.py` vacíos delimitan paquetes. Los de `models/` importan explícitamente el modelo definido en infraestructura. No hacen llamadas de red ni consultas de datos.

Los archivos raíz `apps/branches/views.py` y `apps/shipments/views.py` son restos vacíos del esqueleto generado; las rutas activas utilizan `presentation/api/views.py`. Los `admin.py` generados tampoco registran actualmente modelos de negocio.

## 5. Recorrido de una solicitud

Cuando un cliente llama a un endpoint:

1. Django carga la configuración y las rutas del proyecto.
2. El middleware procesa la solicitud.
3. El resolver identifica la vista y convierte el parámetro UUID cuando corresponde.
4. `APIView` aplica las políticas HTTP configuradas.
5. El método de vista valida entrada con un serializer si la operación recibe cuerpo.
6. La vista construye un DTO y obtiene un servicio mediante una fábrica.
7. El servicio valida o coordina reglas y llama a sus puertos.
8. Los adaptadores ejecutan consultas locales o remotas y devuelven tipos propios.
9. El servicio devuelve un DTO de salida.
10. Un serializer de salida transforma UUID y decimales a su representación JSON.
11. La vista responde con el estado correspondiente o el handler traduce una excepción conocida.

Las fábricas construyen objetos, pero no consultan el proveedor durante el ensamblaje. Por eso una lectura de envíos puede construir un servicio con colaborador de catálogo sin ejecutar una consulta GraphQL.

### 5.1. Fábricas disponibles

| Función | Resultado |
| --- | --- |
| `build_branch_repository()` | `DjangoBranchRepository` con alias `default`. |
| `build_branch_service()` | Contrato `IBranchService`, implementado por `BranchService`. |
| `build_country_catalog()` | Cliente HTTP, mapper y `GraphQLCountryCatalog` conectados con valores de `settings`. |
| `build_shipment_service()` | Contrato `IShipmentService`, implementado por `ShipmentService` con repositorio, verificador de sucursal, catálogo y unidad de trabajo. |

No hay un contenedor de dependencias externo ni un registro de servicios globales con transacciones compartidas. Las fábricas crean las instancias necesarias al atender las solicitudes.

## 6. Contratos y persistencia compartida

### 6.1. `IBaseRepository[T]`

[base_repository_interface.py](../core/application/ports/base_repository_interface.py) declara `save(entity) -> T` y `get_by_id(entity_id: UUID) -> T | None`.

`T` representa una entidad del negocio. El contrato no menciona Django, SQLite ni un modelo ORM. `None` significa ausencia; un fallo de almacenamiento debe informarse como excepción, no como entidad inexistente.

### 6.2. Errores compartidos

En [exceptions.py](../core/application/exceptions.py), `RepositoryError` representa un fallo de persistencia y `RepositoryConflictError` especializa un conflicto de integridad. El consumidor no necesita importar errores Django ni interpretar cadenas de un proveedor SQL.

La causa técnica se conserva mediante encadenamiento de excepciones, útil para diagnóstico interno. El handler HTTP devuelve mensajes controlados en los errores de persistencia previstos.

### 6.3. `RepositoryMapper[T, M]`

Este protocolo está en [base_repository.py](../core/infrastructure/persistence/base_repository.py) porque menciona modelos Django. Declara `to_model(entity)` y `to_domain(model)`.

`T` es la entidad propia; `M` es un subtipo de `models.Model`. La separación permite reutilizar operaciones ORM sin acoplar la aplicación al tipo de tabla.

### 6.4. `BaseRepository[T, M]`

Su constructor recibe:

- `model`: clase ORM concreta.
- `mapper`: conversor de la entidad y ese modelo.
- `db_alias`: entrada de `DATABASES` utilizada por las operaciones.

`save()` construye una instancia ORM y ejecuta `save(using=..., force_insert=True)`. Esa opción exige insertar: no hace un upsert ni actualiza un UUID existente. Convierte el resultado a entidad antes de devolverlo.

`get_by_id()` utiliza el manager por defecto del modelo, selecciona el alias y consulta `pk`. Captura `DoesNotExist` para devolver `None`; otros errores de base se traducen a `RepositoryError`.

La clase no llama a `full_clean()` del modelo ni centraliza reglas de negocio. Las entidades deben ser válidas antes de llegar al repositorio, y las restricciones SQL ofrecen una defensa adicional. Errores de conversión o programación no se capturan indiscriminadamente como fallos de conexión.

## 7. Módulo de sucursales

### 7.1. Inventario de componentes

| Archivo dentro de `apps/branches/` | Contenido |
| --- | --- |
| `domain/entities/branch.py` | Entidad `Branch`. |
| `domain/exceptions.py` | Errores de nombre, ciudad y capacidad. |
| `application/dto/branch_data.py` | `CreateBranchInput`, `UpdateBranchInput`, `BranchData`. |
| `application/dto/branch_info_data.py` | `BranchInfoData` para consulta pública interna. |
| `application/interfaces/branch_service_interface.py` | `IBranchService`. |
| `application/ports/branch_repository_interface.py` | `IBranchRepository`. |
| `application/services/branch_service.py` | Acciones del módulo. |
| `application/exceptions.py` | Sucursal no encontrada durante actualización. |
| `infrastructure/persistence/models/branch_model.py` | Tabla `branches`. |
| `infrastructure/persistence/mappers/branch_mapper.py` | Conversión entidad/ORM. |
| `infrastructure/persistence/repositories/branch_repository.py` | Persistencia y consultas específicas. |
| `presentation/api/serializers.py` | Entrada, actualización y salida HTTP. |
| `presentation/api/views.py` | Listado, creación, PUT y PATCH. |
| `presentation/api/urls.py` | Rutas de sucursales. |

### 7.2. Entidad `Branch`

Es una dataclass inmutable con argumentos por nombre. Sus campos son:

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | `UUID` | Se genera mediante `uuid4` cuando no se proporciona uno al reconstruir. |
| `name` | `str` | Se recortan extremos; entre 1 y 200 caracteres. |
| `city` | `str` | Se recortan extremos; entre 1 y 120 caracteres. |
| `max_weight_kg` | `Decimal` | Finito, positivo, hasta 999999.99 y sin precisión significativa superior a dos decimales. |
| `is_active` | `bool` | Activa por defecto. |

`frozen=True` evita reasignar atributos después de construirla. Durante `__post_init__`, el código utiliza `object.__setattr__` para guardar el nombre y ciudad normalizados.

La capacidad de una sucursal no se limita a 50 kg: ese límite pertenece a cada paquete. Tampoco hay una regla de nombre único, por lo que dos creaciones con los mismos datos pueden producir UUID distintos.

### 7.3. DTO e interfaz

`CreateBranchInput` recibe los cuatro campos editables y asigna estado activo por defecto. `BranchData` agrega el UUID al resultado. Su fábrica `from_entity()` realiza una conversión explícita.

`UpdateBranchInput` declara los campos editables como opcionales, con `None` para indicar que no se enviaron. La API rechaza `null`, de modo que no se confunde ausencia con una solicitud de borrar un valor.

`BranchInfoData` contiene UUID, nombre, estado y capacidad. Se usa para informar a otros módulos; no incluye detalles ORM.

`IBranchService` declara `create`, `list_all`, `get_info` y `update`. `IBranchRepository` hereda el contrato base y agrega `list_all` y `update`.

### 7.4. Creación y consulta

`BranchService.create()` construye `Branch`, ejecutando sus validaciones, llama a `repository.save()` y devuelve `BranchData`.

`list_all()` convierte las entidades devueltas por el repositorio a DTO. El repositorio ordena en SQL por `name` e `id`, materializa la consulta y convierte los modelos a entidades. No hay límite ni paginación.

`get_info()` consulta el repositorio por UUID. Devuelve `None` si no encuentra la sucursal; en caso contrario construye `BranchInfoData`. Este método no tiene un endpoint REST propio en la implementación actual.

### 7.5. Actualización completa y parcial

`BranchUpdateAPIView.put()` utiliza `partial=False`; `patch()` utiliza `partial=True`. Ambos llaman a `_update()` para compartir el flujo HTTP.

El serializer de actualización exige los cuatro campos en PUT. Con PATCH puede faltar cualquiera, pero debe existir al menos uno. En ambos casos rechaza campos desconocidos; no permite modificar el UUID mediante el cuerpo.

El servicio:

1. Busca la sucursal actual.
2. Informa ausencia si no existe.
3. Selecciona únicamente valores del DTO que no sean `None`.
4. Utiliza `dataclasses.replace()` para construir una entidad validada con el mismo UUID.
5. Llama al método `update()` del repositorio.
6. Si la fila dejó de existir antes de escribir, vuelve a informar ausencia.
7. Devuelve el DTO actualizado.

La condición `is not None` conserva correctamente `False` como un cambio válido. Una comparación genérica de valor verdadero descartaría por error una solicitud de inactivación.

El repositorio ejecuta un `UPDATE` por clave primaria sobre los cuatro campos editables. No crea una fila si falta el identificador. `QuerySet.update()` no ejecuta los métodos de guardado del modelo; aquí la validación del dominio ocurre antes de esa escritura explícita.

Un `UpdateBranchInput` vacío usado internamente puede conservar todos los valores; el rechazo de un PATCH HTTP vacío pertenece al serializer. Es importante distinguir el contrato de aplicación de la política HTTP.

### 7.6. Validación HTTP

`CreateBranchSerializer` y `UpdateBranchSerializer` controlan tipos, campos requeridos, longitudes y precisión. `BranchOutputSerializer` devuelve el UUID como texto y la capacidad como cadena decimal.

La creación y actualización no tienen exactamente la misma política de campos extra: el rechazo explícito de desconocidos está implementado en actualización. En creación, los serializers estándar no asignan campos no declarados al DTO.

## 8. Módulo de envíos

### 8.1. Inventario de componentes

| Archivo dentro de `apps/shipments/` | Contenido |
| --- | --- |
| `domain/value_objects/package_weight.py` | Peso validado e inmutable. |
| `domain/entities/shipment.py` | Entidad `Shipment`. |
| `domain/exceptions.py` | Errores de peso y datos de envío. |
| `application/dto/shipment_data.py` | Entrada de creación y resultado completo. |
| `application/dto/branch_info_data.py` | Representación de sucursal propia del consumidor. |
| `application/dto/country_data.py` | Datos mínimos de país. |
| `application/interfaces/shipment_service_interface.py` | `IShipmentService`. |
| `application/ports/` | Repositorio, verificador de sucursal, catálogo y unidad de trabajo. |
| `application/services/shipment_service.py` | Creación, listado y detalle. |
| `application/exceptions.py` | Fallos esperados de coordinación. |
| `infrastructure/persistence/` | Modelo, mapper, repositorio y transacción. |
| `infrastructure/integrations/branches/` | Consulta interna a sucursales. |
| `infrastructure/integrations/countries_api/` | Consulta, cliente, catálogo y mapper GraphQL. |
| `presentation/api/` | Serializers, vistas, rutas y handler. |

### 8.2. Objeto de valor `PackageWeight`

Recibe `kg: Decimal`. Su constructor rechaza valores que no sean `Decimal`, valores no finitos, cero, negativos, más de 50 kg y valores que requerirían redondeo significativo a dos decimales.

No convierte un `float` directamente ni corrige un peso inválido. En HTTP, `DecimalField` transforma la representación recibida al tipo que espera el dominio. Al recuperar un envío, el mapper vuelve a construir `PackageWeight` con el valor de almacenamiento.

### 8.3. Entidad `Shipment`

| Campo | Propósito |
| --- | --- |
| `id` | Identidad UUID local del envío. |
| `origin_branch_id` | Referencia UUID a la sucursal validada. |
| `origin_branch_name` | Nombre histórico de la sucursal, no una consulta dinámica. |
| `description` | Texto recortado, entre 1 y 500 caracteres. |
| `weight` | Instancia válida de `PackageWeight`. |
| `destination_country_code` | Código de dos letras ASCII, normalizado a mayúsculas. |
| `destination_country_name` | Nombre del país al crear el registro, hasta 200 caracteres. |
| `currency` | Información de moneda no vacía, hasta 100 caracteres. |
| `status` | Únicamente `CREATED` en el alcance implementado. |

El nombre de sucursal debe ser no vacío y de hasta 200 caracteres. La entidad valida que el peso sea un objeto de valor y que el estado corresponda al alcance actual. No hay fechas de creación ni un ciclo de estados de seguimiento implementado.

La inmutabilidad impide modificar directamente estos valores. No se ofrece edición de envíos por la API.

### 8.4. Entrada y salida de aplicación

`CreateShipmentInput` recibe `origin_branch_id`, `description`, `weight_kg` y `destination_country_code`. No acepta identificador de envío, nombres históricos, moneda ni estado como decisiones del cliente.

`ShipmentData` devuelve esos datos resueltos, con `weight_kg` plano en lugar de exponer el objeto `PackageWeight`. Se construye mediante `from_entity()`.

`CountryDataDTO` contiene `code`, `name` y `currency`. `BranchInfoDTO` contiene `id`, `name`, `is_active` y `max_weight_kg`. No incorporan respuestas HTTP ni estructuras GraphQL.

### 8.5. Puertos de salida

| Puerto | Operación | Significado de ausencia o error |
| --- | --- | --- |
| `IShipmentRepository` | `save`, `get_by_id`, `list_all`. | Recuperación sin coincidencia devuelve `None`; fallo de persistencia lanza error propio. |
| `IBranchChecker` | `get_branch_info`. | `None` significa sucursal inexistente. |
| `ICountryCatalog` | `get_country`. | `None` significa país ausente confirmado; indisponibilidad es excepción. |
| `IUnitOfWork` | `__enter__`, `__exit__`. | Delimita confirmación o rollback y conserva propagación de excepciones. |

### 8.6. Creación paso a paso

`ShipmentService.create()` realiza este recorrido:

1. Construye `PackageWeight` antes de acceder a sucursales, red o escritura.
2. Normaliza y verifica el formato del código del país.
3. Consulta `IBranchChecker` con el UUID de origen.
4. Rechaza sucursal inexistente o inactiva.
5. Compara el peso con la capacidad de esa sucursal.
6. Consulta `ICountryCatalog` con el código normalizado.
7. Rechaza ausencia confirmada de país; deja propagarse su indisponibilidad como error conocido.
8. Entra en la unidad de trabajo local.
9. Construye `Shipment` con datos validados e instantáneas.
10. Inserta mediante el repositorio y convierte a `ShipmentData`.
11. Sale del bloque transaccional y devuelve el DTO después de confirmar correctamente.

Un peso inválido no debe llamar a otros puertos. Una sucursal inválida no debe consultar el país. Un proveedor indisponible no debe producir un envío parcial.

La validación HTTP de la descripción ocurre antes de invocar el servicio. Si se llama al servicio directamente, la validación final de esa descripción también ocurre al construir la entidad dentro de la unidad de trabajo; no debe asumirse que todo campo ya fue comprobado por el transporte HTTP.

### 8.7. Lecturas locales

`list_all()` solicita entidades al repositorio y las convierte a DTO; el repositorio ordena por UUID. `get_by_id()` devuelve un DTO o lanza `ShipmentNotFoundError` si el repositorio devuelve `None`.

Ninguna lectura consulta el catálogo ni vuelve a validar sucursal activa o capacidad actual. Un envío histórico sigue legible aunque se renombre o inactive su sucursal. La ordenación UUID no equivale a una cronología, porque se generan UUID aleatorios y no existe un campo temporal de ordenación.

## 9. Comunicación entre módulos

En [local_branch_checker.py](../apps/shipments/infrastructure/integrations/branches/local_branch_checker.py), `LocalBranchChecker` recibe `IBranchService` por constructor.

Su método `get_branch_info()` llama a `service.get_info()`. Si recibe `None`, conserva la ausencia; de lo contrario transforma `BranchInfoData` en `BranchInfoDTO`.

El adaptador es el único punto de esta colaboración que conoce el contrato público de sucursales. La aplicación de envíos no importa `BranchService`, `BranchModel`, el repositorio de sucursales ni un cliente HTTP interno.

Existen dos excepciones de nombre `BranchNotFoundError` en módulos diferentes. Una pertenece a actualización de sucursales y otra a creación de envíos; sus espacios de nombres y handlers mantienen su propiedad. El DTO y las excepciones de un consumidor no deben confundirse con acceso libre a la implementación del otro módulo.

## 10. Catálogo GraphQL

### 10.1. Consulta y transporte

La consulta vive en `queries/get_country.py` como una cadena Python:

```graphql
query GetCountry($code: ID!) {
  country(code: $code) {
    code
    name
    currency
  }
}
```

El cliente envía un POST con las claves `query` y `variables`; esta última contiene el código recibido, por ejemplo `{"code": "CR"}`. No concatena el código dentro de la consulta.

`CountryGraphQLClient.execute()` utiliza `requests.post()` con URL y tupla de timeout inyectadas. Primero comprueba el estado HTTP; después interpreta JSON. Su implementación es síncrona y no añade reintentos, caché ni una sesión HTTP persistente propia.

### 10.2. Clasificación de la respuesta

| Respuesta o problema | Tratamiento |
| --- | --- |
| Timeout o error de conexión | `CountryCatalogUnavailableError`. |
| HTTP de error | `raise_for_status()` provoca traducción a indisponibilidad. |
| Cuerpo no JSON | Se traduce el error de lectura a indisponibilidad. |
| JSON que no es un objeto | Respuesta inválida. |
| Clave `errors` presente | Se rechaza, incluso con datos parciales o lista de errores vacía. |
| `data` ausente o sin objeto | Respuesta inválida. |
| `country` ausente dentro de `data` | Contrato inválido, no ausencia de país. |
| `country: null` con el resto válido | El catálogo devuelve `None`; el servicio responde país inexistente. |
| País con campos válidos | Se devuelve `CountryDataDTO`. |

### 10.3. Mapper anticorrupción

`CountryGraphQLMapper.to_dto()` exige un objeto de país, coincidencia de código con el solicitado, nombre no vacío hasta 200 caracteres y moneda no vacía hasta 100. Recorta nombre y moneda.

No inventa una moneda cuando el proveedor devuelve `null`. Tampoco interpreta la cadena de moneda como si siempre representara exactamente una sola divisa. Solo conserva la información necesaria para el envío.

`GraphQLCountryCatalog` coordina consulta, comprobación de ausencia y mapper. El servicio recibe datos propios o un error conocido, no diccionarios GraphQL ni excepciones de `requests`.

### 10.4. Dependencias de red reales

Crear un envío válido necesita acceso al proveedor. Las consultas de envíos y la suite automatizada no lo necesitan. La disponibilidad real del endpoint no pudo comprobarse desde el entorno de implementación; esa limitación no se resuelve simulando un país dentro del código de producción.

## 11. Tablas, modelos y migraciones

### 11.1. Tabla `branches`

| Columna | Modelo Django | Detalle |
| --- | --- | --- |
| `id` | `UUIDField(primary_key=True)` | UUID generado si el modelo se construye sin uno. |
| `name` | `CharField(200)` | Nombre de la sucursal. |
| `city` | `CharField(120)` | Ciudad de ubicación. |
| `max_weight_kg` | `DecimalField(8, 2)` | Capacidad por paquete. |
| `is_active` | `BooleanField` | Activa por defecto. |

`branch_capacity_positive` exige capacidad mayor que cero. La ordenación por defecto del modelo es nombre y UUID; el repositorio de listado también la declara explícitamente.

### 11.2. Tabla `shipments`

| Columna | Modelo Django | Detalle |
| --- | --- | --- |
| `id` | `UUIDField(primary_key=True)` | Identidad del envío. |
| `origin_branch_id` | `UUIDField` | Referencia sin FK. |
| `origin_branch_name` | `CharField(200)` | Instantánea del nombre de origen. |
| `description` | `CharField(500)` | Descripción del paquete. |
| `weight_kg` | `DecimalField(8, 2)` | Valor almacenado del objeto de peso. |
| `destination_country_code` | `CharField(2)` | Código del país. |
| `destination_country_name` | `CharField(200)` | Nombre histórico del país. |
| `currency` | `CharField(100)` | Información histórica de moneda. |
| `status` | `CharField(20)` | Por defecto `CREATED`. |

`shipment_weight_valid` exige peso mayor que cero y menor o igual a 50. No comprueba capacidad de otra fila ni estado activo de sucursal. El catálogo externo no se copia como una tabla local de países.

### 11.3. Mappers y descubrimiento

`BranchMapper` y `ShipmentMapper` preservan el UUID en ambas direcciones. El primero copia los campos de sucursal; el segundo convierte `weight.kg` a columna y reconstruye `PackageWeight` al leer.

Los paquetes raíz `apps/<módulo>/models/__init__.py` importan sus modelos de infraestructura y los exponen mediante `__all__`. Esto permite que Django descubra los modelos aunque sus implementaciones estén organizadas por capas.

Si los datos guardados incumplieran reglas del dominio, reconstruir una entidad puede fallar. Los mappers no deben ocultar esa inconsistencia devolviendo valores inventados.

### 11.4. Migraciones

Cada app dispone de `migrations/0001_initial.py`. Se generaron con Django y crean su tabla con las restricciones correspondientes. Las migraciones estándar de Django siguen existiendo para autenticación, sesiones, administración y tipos de contenido.

Para revisar y evolucionar el esquema:

```powershell
.\env\Scripts\python.exe manage.py showmigrations
.\env\Scripts\python.exe manage.py makemigrations branches shipments
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Genera nuevas migraciones cuando cambien modelos; no edites migraciones aplicadas para simular un esquema nuevo. El código Python y las migraciones se versionan; la base local no.

## 12. Transacciones y concurrencia

### 12.1. Unidad de trabajo

`IUnitOfWork` declara el protocolo de context manager y exige no suprimir excepciones. `DjangoUnitOfWork` guarda el alias y administra un contexto `transaction.atomic()`.

Al entrar, impide reentrar con la misma instancia si ya está activa. Al salir, entrega a Django la excepción del bloque, limpia su referencia interna y devuelve `False`. Los errores de base al iniciar o finalizar se traducen a `RepositoryError`.

Una instancia puede reutilizarse después de terminar, pero no debe compartirse entre solicitudes concurrentes. La fábrica crea una unidad para cada servicio ensamblado.

### 12.2. Qué queda dentro de la transacción

En la creación de envíos, la consulta remota ocurre antes del `with`. Dentro quedan construcción final, inserción y preparación del DTO. El retorno al consumidor ocurre después de salir correctamente del contexto.

La transacción no coordina un commit con el proveedor GraphQL ni ofrece atomicidad distribuida. Tampoco protege automáticamente todos los datos consultados anteriormente.

La creación de una sucursal es una sola escritura. Su actualización usa una instrucción SQL explícita. Esos servicios no introducen otra unidad de trabajo abstracta para una coordinación multioperación que no necesitan en el alcance actual.

### 12.3. Garantías que todavía no existen

No se implementaron bloqueos de recursos para cambios concurrentes, tokens de versión, idempotencia de solicitudes ni detección de actualización perdida. Un PATCH lee la fila, reconstruye la entidad y escribe sus campos; otra escritura entre esas etapas puede ser sobrescrita.

Si el registro se elimina entre lectura y actualización, el repositorio informa `None` y el servicio devuelve ausencia. Ese control no equivale a resolver todas las carreras concurrentes.

## 13. Contrato HTTP y ejemplos

### 13.1. Rutas disponibles

| Método | Ruta | Éxito | Resultado |
| --- | --- | --- | --- |
| GET | `/api/branches/` | `200` | Lista JSON de sucursales. |
| POST | `/api/branches/` | `201` | Sucursal creada. |
| PUT | `/api/branches/{id}/` | `200` | Sucursal actualizada con cuerpo completo. |
| PATCH | `/api/branches/{id}/` | `200` | Sucursal actualizada parcialmente. |
| GET | `/api/shipments/` | `200` | Lista JSON de envíos. |
| POST | `/api/shipments/` | `201` | Envío creado. |
| GET | `/api/shipments/{id}/` | `200` | Detalle de envío. |

Conserva las barras finales al enviar solicitudes. Los parámetros de detalle usan el conversor UUID de Django. No hay GET de sucursal individual, DELETE de negocio, PUT de envíos ni rutas `/getall`: el GET sobre la colección realiza el listado.

Además existen `/api/docs/`, `/api/schema/` y la ruta estándar `/admin/`. La administración no representa un panel funcional de sucursales y envíos: los modelos no se registraron allí.

### 13.2. Crear una sucursal

Cuerpo para POST:

```json
{
  "name": "Sucursal Managua",
  "city": "Managua",
  "max_weight_kg": "25.00",
  "is_active": true
}
```

`is_active` puede omitirse al crear y toma `true`. Los demás campos son obligatorios. Una respuesta ilustrativa es:

```json
{
  "id": "0f0ebf04-bd30-4d27-a797-d49c8f35a480",
  "name": "Sucursal Managua",
  "city": "Managua",
  "max_weight_kg": "25.00",
  "is_active": true
}
```

El UUID del ejemplo no garantiza un registro existente; utiliza el que devuelva tu servidor. Repetir el POST puede crear otra sucursal con el mismo nombre.

### 13.3. Actualizar sucursales

PUT exige el cuerpo completo con `name`, `city`, `max_weight_kg` e `is_active`, aunque solo quieras cambiar uno de ellos. PATCH permite este cuerpo:

```json
{
  "city": "Leon",
  "is_active": false
}
```

Los demás campos se conservan. `{}`, `{"name": null}`, campos desconocidos o un intento de cambiar `id` en actualización se rechazan con `400`. Una capacidad decimal válida en formato, pero igual a cero, se rechaza con `422` y no guarda el resto de los cambios del cuerpo.

### 13.4. Crear un envío

Cuerpo para POST, sustituyendo el UUID:

```json
{
  "origin_branch_id": "0f0ebf04-bd30-4d27-a797-d49c8f35a480",
  "description": "Documentos",
  "weight_kg": "2.50",
  "destination_country_code": "CR"
}
```

Los cuatro campos son obligatorios. La entrada admite código de país en minúsculas y lo normaliza; exige dos letras ASCII. La validación del catálogo confirma existencia, no solo formato.

Respuesta ilustrativa:

```json
{
  "id": "d43933f8-5c2d-4105-8b4e-7f86ca3977f7",
  "origin_branch_id": "0f0ebf04-bd30-4d27-a797-d49c8f35a480",
  "origin_branch_name": "Sucursal Managua",
  "description": "Documentos",
  "weight_kg": "2.50",
  "destination_country_code": "CR",
  "destination_country_name": "Costa Rica",
  "currency": "CRC",
  "status": "CREATED"
}
```

Nombre y moneda dependen del proveedor; no deben fijarse en la vista para reproducir este ejemplo. El envío no contiene tarifa, fecha de entrega o seguimiento porque esas funciones no están implementadas.

### 13.5. Listados y representación

Las colecciones devuelven un array, incluido `[]` si no hay registros. No usan una envoltura `results`, contadores ni enlaces de paginación. Las salidas representan decimales como cadenas, por ejemplo `"2.50"`, y UUID como texto.

La vista GET de envíos no llama al catálogo; los datos guardados permiten consultar historial aunque falle internet. La disponibilidad de SQLite sigue siendo necesaria.

## 14. Errores y respuestas

### 14.1. Catálogo de errores previstos

| Código JSON | Estado | Situación |
| --- | --- | --- |
| `invalid_request` | `400` | Error de validación DRF. |
| `invalid_branch` | `422` | Regla de la entidad de sucursal incumplida. |
| `branch_not_found` | `404` | Sucursal ausente durante actualización o creación de envío. |
| `branch_inactive` | `422` | Sucursal inactiva al crear envío. |
| `branch_capacity_exceeded` | `422` | Peso superior a la capacidad del origen. |
| `invalid_shipment` | `422` | Peso o dato de dominio del envío inválido. |
| `country_not_found` | `404` | Ausencia de país confirmada por el proveedor. |
| `shipment_not_found` | `404` | UUID de envío sin coincidencia local. |
| `country_catalog_unavailable` | `503` | Fallo de transporte o respuesta externa inválida. |
| `persistence_conflict` | `409` | Restricción de integridad impide guardar. |
| `persistence_unavailable` | `503` | Consulta, escritura o transacción no pudo completarse. |
| `http_error` | Variable | Otros errores estándar gestionados por DRF, como un método no permitido. |

La distinción `400`/`422` depende de la frontera que detecta el problema. `"abc"` en peso no tiene formato decimal y da `400`; `"51.00"` tiene formato válido, pero incumple el dominio y da `422`.

### 14.2. Estructura de los cuerpos

Error de negocio:

```json
{
  "code": "branch_capacity_exceeded",
  "detail": "El peso supera la capacidad de la sucursal."
}
```

Error de formato, con detalle ilustrativo por campo:

```json
{
  "code": "invalid_request",
  "detail": "Solicitud inválida.",
  "errors": {
    "origin_branch_id": ["Valor UUID inválido."]
  }
}
```

El texto exacto de validaciones estándar puede depender del idioma y del framework. Es preferible usar estado y `code` para decisiones del cliente y mostrar `detail` como explicación.

### 14.3. Encadenamiento de handlers

El handler de envíos reconoce sus excepciones de aplicación y dominio. Cuando no aplica, delega al handler general, que reconoce sucursales y errores compartidos y después llama al handler estándar de DRF.

Si el framework no reconoce un error inesperado, devuelve `None` para su tratamiento como fallo interno. En desarrollo, `DEBUG` puede mostrar información de diagnóstico; no debe interpretarse como el contrato de errores públicos previsto.

Un UUID mal formado en una ruta no pasa el conversor de Django y puede devolver el `404` estándar antes de entrar a DRF. Por eso no todos los errores de enrutamiento tienen necesariamente el mismo cuerpo JSON que una ausencia encontrada dentro del servicio.

## 15. Documentación OpenAPI y Scalar

### 15.1. Esquema local

[openapi.json](../config/openapi.json) declara OpenAPI 3.0.3, información del proyecto, servidor relativo `/`, etiquetas y las siete operaciones distribuidas en cuatro patrones de ruta.

Sus componentes son `CreateBranchRequest`, `UpdateBranchRequest`, `PatchBranchRequest`, `Branch`, `CreateShipmentRequest`, `Shipment` y `Error`. Las respuestas de error se reutilizan mediante referencias internas.

POST tiene entradas distintas de sus salidas: el servidor genera identidades y resuelve datos externos. PUT declara cuatro campos obligatorios; PATCH no los exige individualmente, pero requiere al menos uno y prohíbe propiedades desconocidas.

Este contrato se mantiene manualmente. No se genera automáticamente con `drf-spectacular`; ese paquete no está instalado. Cada cambio de rutas, serializers o respuestas requiere revisar el JSON.

### 15.2. Vistas de documentación

`openapi_schema()` lee el archivo UTF-8, interpreta JSON y devuelve `JsonResponse`. No consulta tablas ni servicios externos. `api_docs()` renderiza la plantilla con la ruta obtenida mediante `reverse('openapi-schema')`.

Ambas usan `require_safe`, por lo que aceptan GET y HEAD, no POST. No añaden operaciones de negocio a la API.

### 15.3. Interfaz Scalar

[api_docs.html](../templates/api_docs.html) contiene una cabecera, enlace al esquema, mensaje de carga y contenedor de la interfaz. `json_script` entrega la URL al JavaScript como datos JSON seguros.

El módulo JavaScript importa Scalar desde jsDelivr y lo monta contra `/api/schema/`. `proxyUrl` está vacío: las llamadas de API no pasan por un proxy Scalar externo. El servidor relativo hace que las peticiones se dirijan al mismo host de la documentación.

Si la importación del CDN falla, se muestra un mensaje y permanece el enlace al esquema. Obtener HTML con `200` no prueba por sí solo que el navegador haya descargado y renderizado el recurso externo. Esa carga visual no se verificó en el entorno de implementación.

## 16. Pruebas

### 16.1. Distribución actual

| Archivo de pruebas | Casos |
| --- | --- |
| `apps/branches/tests/application/test_branch_service.py` | 8 |
| `apps/branches/tests/domain/test_branch.py` | 2 |
| `apps/branches/tests/infrastructure/test_repository.py` | 4 |
| `apps/branches/tests/presentation/test_api.py` | 9 |
| `apps/shipments/tests/application/test_shipment_service.py` | 11 |
| `apps/shipments/tests/domain/test_weight.py` | 2 |
| `apps/shipments/tests/infrastructure/test_branch_checker.py` | 2 |
| `apps/shipments/tests/infrastructure/test_country_catalog.py` | 6 |
| `apps/shipments/tests/infrastructure/test_repository.py` | 3 |
| `apps/shipments/tests/presentation/test_api.py` | 11 |
| `config/tests/test_api_docs.py` | 6 |
| **Total de métodos de prueba** | **64** |

Algunos métodos agrupan escenarios mediante `subTest`, de modo que el número de comprobaciones individuales es mayor. No se fija un porcentaje numérico de cobertura.

### 16.2. Qué demuestra cada nivel

Las pruebas de dominio usan `unittest.TestCase` y verifican límites, inmutabilidad e identidad sin base de datos. Las de servicios inyectan puertos sustitutos y verifican respuestas y ausencia de llamadas cuando una validación falla.

Persistencia comprueba identidad, decimales, listados, conflictos y rollback real. Para observar límites transaccionales se usa `TransactionTestCase`; otras pruebas con base utilizan el aislamiento de `TestCase` o `APITestCase`.

Las pruebas GraphQL simulan el transporte, incluidos timeout, HTTP fallido, JSON inválido, datos parciales y país nulo. Las pruebas de API mantienen servicio y persistencia reales y sustituyen el catálogo. También comprueban que actualizar sucursales no reescriba instantáneas de envíos.

Las pruebas de documentación verifican HTML, esquema, rutas y métodos reales, referencias internas, entradas obligatorias, campos de serializers y forma de las respuestas declaradas. No reemplazan una inspección visual en navegador ni constituyen una validación exhaustiva de todas las reglas de OpenAPI.

### 16.3. Comandos

```powershell
.\env\Scripts\python.exe manage.py test
```

Para investigar un área concreta:

```powershell
.\env\Scripts\python.exe manage.py test apps.branches --verbosity 2
.\env\Scripts\python.exe manage.py test apps.shipments.tests.application --verbosity 2
.\env\Scripts\python.exe manage.py test config.tests --verbosity 2
```

El comando completo incluye documentación; ejecutar solo ambas apps no incluye `config/tests/`. No necesitas internet para la suite. La base de pruebas se crea separada de `db.sqlite3` y se elimina al terminar según el comportamiento del runner.

## 17. Diagnóstico y mantenimiento

### 17.1. Comprobar estado local

```powershell
.\env\Scripts\python.exe manage.py check
.\env\Scripts\python.exe manage.py showmigrations
.\env\Scripts\python.exe manage.py makemigrations --check --dry-run
.\env\Scripts\python.exe -m pip check
```

Estos comandos revisan configuración, migraciones y coherencia de dependencias; no demuestran que el proveedor remoto esté disponible ni que exista capacidad suficiente para una carga productiva.

### 17.2. Revisar datos desde el shell

Puedes abrir `manage.py shell` y consultar modelos para diagnóstico. Ese acceso ORM es una herramienta técnica; no justifica introducir consultas directas a tablas en vistas o servicios del núcleo.

No es necesario añadir un endpoint de negocio para inspeccionar un conteo durante desarrollo. Evita convertir los comandos de diagnóstico en scripts que borren o reconstruyan datos existentes sin una necesidad explícita.

### 17.3. Agregar una acción

1. Define la acción y sus reglas antes de crear rutas.
2. Añade o ajusta el DTO de entrada/salida.
3. Actualiza la interfaz pública del servicio.
4. Implementa la coordinación en el servicio del módulo.
5. Si necesitas otra capacidad de persistencia o integración, define su puerto y adaptador.
6. Implementa serializer, vista y ruta de presentación.
7. Actualiza fábricas si cambian dependencias.
8. Genera migración si cambia el esquema de datos.
9. Actualiza OpenAPI, ejemplos y estos manuales.
10. Completa pruebas de comportamiento y ejecuta las comprobaciones pertinentes.

No agregues una clase por acción debajo de un servicio existente sin una razón de diseño. Tampoco publiques un CRUD completo solo porque una abstracción base lo permita.

### 17.4. Archivos que se conservan y excluyen

Versiona código, migraciones, documentación, `requirements.txt`, `.env.example`, plantilla Scalar y OpenAPI. Excluye `.env`, `env/`, `db.sqlite3` y cachés de Python.

Desde la raíz del proyecto Git puedes revisar `git status --short` y `git check-ignore .env env/ db.sqlite3`. No publiques valores privados para demostrar que la configuración funciona.

## 18. Límites y evolución

### 18.1. Alcance actual

La demo no implementa autenticación de negocio, permisos por usuario, frontend de logística, eliminación, edición de envíos, tarifas, seguimiento, idempotencia, colas ni paginación. La administración Django existe como ruta estándar, sin registrar los modelos de negocio.

Los listados cargan todos los registros y reconstruyen entidades. Es una simplificación para un volumen pequeño; no es una estrategia de informes masivos. Cuando el volumen lo requiera, filtros, paginación y proyecciones deben aplicarse en base de datos antes de materializar resultados.

### 18.2. Independencia del motor

Los contratos de repositorio y unidad de trabajo protegen la aplicación de detalles concretos. Sin embargo, cambiar SQLite por PostgreSQL o SQL Server requiere elegir backend y drivers compatibles, revisar versiones, preparar esquema y traslado de datos y comprobar precisión, restricciones y concurrencia.

SQLite no ofrece exactamente las mismas características que otros motores, incluido el tratamiento interno de decimales y las garantías disponibles para concurrencia. Las pruebas actuales en SQLite no certifican comportamiento equivalente en otro motor.

### 18.3. Operación y despliegue

`runserver` se utiliza para desarrollo. Para desplegar se necesita una configuración específica de servidor, hosts, secretos, depuración, archivos estáticos, acceso a red y base de datos. El proyecto no contiene una receta de infraestructura productiva ya validada.

La configuración de las capas no sustituye medición de rendimiento, políticas de seguridad o pruebas de carga. Las futuras mejoras deben responder a necesidades observadas, conservando contratos claros y sin añadir complejidad que la demo todavía no necesita.
