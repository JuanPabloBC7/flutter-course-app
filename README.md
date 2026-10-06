# flutter_course_backend

API REST para la gestión de tarjetas de crédito. Permite listar, consultar,
crear, actualizar y eliminar lógicamente tarjetas, con validación de numeración
(Luhn), marca, fecha de vencimiento y CVV.

> Ámbito: administración de tarjetas y sus límites de crédito. **No** procesa
> pagos ni cobros reales.

## Stack tecnológico

| Componente     | Elección            | Motivo                                              |
|----------------|---------------------|-----------------------------------------------------|
| Runtime        | Node.js >= 20       | LTS, soporte nativo de `node:crypto`.               |
| Lenguaje       | TypeScript 5 strict | Tipado estricto, `any` evitado.                     |
| Framework HTTP | Express 4           | Simple, maduro, fácil de probar.                    |
| Base de datos  | PostgreSQL + `pg`   | Consultas parametrizadas, sin ORM pesado.           |
| Validación     | zod                 | Validación declarativa y segura de entradas.        |
| Pruebas        | Jest + supertest    | Unitarias (validación) e integración (endpoints).   |

Se eligió `pg` con SQL parametrizado en lugar de un ORM para mantener el proyecto
ligero, transparente y fácil de auditar. La lógica de negocio (service) está
separada de la persistencia (repository).

## Arquitectura

```
src/
├── config/        Validación y carga de variables de entorno (zod)
├── database/      Pool de conexiones, migraciones y runner
├── types/         Interfaces y tipos del dominio
├── validation/    Validación de tarjetas (Luhn, marca, fecha, CVV) + esquemas zod
├── security/      Huella criptográfica (HMAC) de tarjetas
├── repositories/  Acceso a PostgreSQL (SQL parametrizado)
├── services/      Lógica de negocio
├── controllers/   Manejo de request/response HTTP
├── middleware/    Validación y manejo centralizado de errores
├── routes/        Definición de endpoints (/api/v1)
├── app.ts         Construcción de la app Express (exportable para tests)
└── server.ts      Arranque del servidor + apagado ordenado
tests/             Pruebas unitarias y de integración
```

## Requisitos

- Node.js 20 o superior.
- PostgreSQL 13 o superior (local o remoto).

> Verifica tu entorno con `node --version` y `psql --version`.

## Instalación

```bash
cd credit-cards-api
npm install
```

## Configuración

Copia el archivo de ejemplo y ajusta los valores:

```bash
cp .env.example .env
```

Variables principales (ver `.env.example` para la lista completa):

| Variable                  | Descripción                                        |
|---------------------------|----------------------------------------------------|
| `PORT`                    | Puerto HTTP (por defecto 4000).                    |
| `PGHOST` … `PGDATABASE`   | Conexión a PostgreSQL.                             |
| `CORS_ORIGINS`            | Orígenes permitidos, separados por coma. Vacío = CORS deshabilitado. |
| `CARD_FINGERPRINT_SECRET` | Secreto (>= 16 chars) para la huella HMAC de tarjetas. |

La aplicación **valida la configuración al arrancar** y no inicia si falta o es
inválida alguna variable.

## Base de datos y migraciones

Crea las bases de datos (desarrollo y pruebas):

```bash
createdb credit_cards
createdb credit_cards_test
```

Aplica las migraciones:

```bash
npm run migrate
```

El runner es idempotente y registra lo aplicado en la tabla `schema_migrations`.

### Esquema

Tabla `credit_cards`:

| Columna            | Tipo             | Notas                                       |
|--------------------|------------------|---------------------------------------------|
| `id`               | UUID (PK)        | `gen_random_uuid()`.                        |
| `user_id`          | TEXT NOT NULL    | Identificador del propietario.              |
| `card_fingerprint` | TEXT NOT NULL    | HMAC-SHA256 del PAN (sin guardar el PAN).   |
| `last4`            | CHAR(4) NOT NULL | Últimos 4 dígitos.                          |
| `brand`            | enum `card_brand`| `VISA` \| `MASTERCARD`.                     |
| `credit_limit`     | NUMERIC(14,2)    | `CHECK >= 0`.                               |
| `expiration_month` | SMALLINT         | `CHECK 1..12`.                              |
| `expiration_year`  | SMALLINT         | `CHECK 1970..2100`.                         |
| `status`           | enum `card_status`| `ACTIVE` \| `BLOCKED` \| `EXPIRED`.        |
| `created_at`       | TIMESTAMPTZ      | `now()`.                                    |
| `updated_at`       | TIMESTAMPTZ      | `now()`.                                    |
| `deleted_at`       | TIMESTAMPTZ NULL | Soft delete. NULL = vigente.                |

Índices: parcial por `user_id` para tarjetas vigentes y único parcial
`(user_id, card_fingerprint)` sobre filas no eliminadas, para evitar duplicados.

### Sobre `userId` (no existe tabla de usuarios)

Este proyecto se creó de forma aislada y **no hay un sistema de usuarios en el
workspace**. Por eso `user_id` es un `TEXT` que recibe el identificador tal cual
lo envía el cliente. La API **no comprueba** que el usuario exista ni valida su
identidad. Si en el futuro se integra una tabla `users`, debe convertirse en una
clave foránea real (`REFERENCES users(id)`) y añadirse la validación
correspondiente.

## Ejecución

Modo desarrollo (recarga automática):

```bash
npm run dev
```

Compilar y ejecutar en producción:

```bash
npm run build
npm start
```

Comprobación rápida:

```bash
curl http://localhost:4000/health
# -> {"status":"ok"}
```

## Endpoints

Prefijo: `/api/v1`. Las respuestas exitosas usan el envoltorio `{ "data": ... }`.

| Método | Ruta                     | Descripción                        | Éxito |
|--------|--------------------------|------------------------------------|-------|
| GET    | `/credit-cards`          | Lista tarjetas activas.            | 200   |
| GET    | `/credit-cards/:id`      | Obtiene una tarjeta por id.        | 200   |
| POST   | `/credit-cards`          | Crea una tarjeta.                  | 201   |
| PATCH  | `/credit-cards/:id`      | Actualiza `creditLimit`/`status`.  | 200   |
| DELETE | `/credit-cards/:id`      | Eliminación lógica.                | 204   |

Códigos de error: `400` (entrada inválida), `404` (no existe/eliminada),
`409` (duplicado), `500` (error interno). Formato uniforme:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La solicitud contiene datos inválidos",
    "details": [
      { "field": "creditLimit", "message": "creditLimit no puede ser negativo" }
    ]
  }
}
```

Ejemplos de solicitudes: ver [`docs/curl-examples.md`](docs/curl-examples.md) y
la colección de Postman en [`docs/postman_collection.json`](docs/postman_collection.json).

## Validación de tarjetas

El módulo `src/validation/card-validator.ts` implementa:

- Limpieza de espacios y guiones; rechazo de caracteres no numéricos.
- Algoritmo de **Luhn**.
- Detección de **marca** centralizada: VISA (prefijo `4`) y Mastercard
  (`51–55` y `2221–2720`).
- Longitudes por marca (VISA: 13/16/19; Mastercard: 16).
- **Vencimiento**: mes 1–12, válida hasta el último día del mes de vencimiento.
- **CVV**: numérico, 3 dígitos para Visa/Mastercard.

### Alcance real de la validación

Estas validaciones comprueban **únicamente formato, numeración, checksum, marca
y fecha**. **No** prueban que la tarjeta exista, esté emitida, pertenezca al
usuario, esté activa en la red de pagos o tenga crédito disponible. Para eso se
requiere una integración autorizada con un proveedor de pagos o el emisor.

## Protección de datos sensibles

- El **número completo (PAN) nunca se almacena**: solo se guardan `last4` y una
  **huella HMAC-SHA256** (`card_fingerprint`) para detectar duplicados.
- El **CVV nunca se persiste** ni se devuelve; solo vive en memoria durante la
  validación de la solicitud.
- Las respuestas **no exponen** PAN, CVV ni la huella.
- Los logs y mensajes de error **no incluyen** datos sensibles ni SQL interno.
- Consultas **parametrizadas** en todo el acceso a datos.
- Límite de tamaño del cuerpo de la solicitud (10 KB).
- CORS **explícito**: solo los orígenes configurados; deshabilitado si la lista
  está vacía.

### Aviso PCI DSS

La huella HMAC es una **referencia interna** para correlación local; **no** es
tokenización de un proveedor de pagos ni implica cumplimiento PCI DSS. Una
integración real con tarjetas de pago debe delegar el manejo del PAN a un
proveedor certificado (que devuelve un token) y considerar los requisitos
**PCI DSS** y las responsabilidades del proveedor.

### Autenticación

Por simplicidad, los endpoints **no incluyen autenticación/autorización**. Antes
de exponerlos en un entorno real deben protegerse con autenticación y
autorización (por ejemplo, verificando que el usuario sea dueño de la tarjeta).

## Pruebas

```bash
# Solo unitarias (no requieren base de datos)
npm run test:unit

# Todas (unitarias + integración)
NODE_ENV=test PGDATABASE=credit_cards_test npm test
```

- **Unitarias** (`tests/card-validator.test.ts`): Luhn, marca (VISA y Mastercard
  en ambos rangos), vencimiento y CVV. No requieren base de datos.
- **Integración** (`tests/credit-cards.integration.test.ts`): recorren los cinco
  endpoints con `supertest` contra una base de datos de **pruebas** aislada.
  Si no hay base de datos accesible, **la suite se omite con un aviso** (no se
  simulan resultados exitosos).

### Resultados en este entorno

En la máquina donde se desarrolló **no hay PostgreSQL instalado**, por lo que:

- `npm run test:unit` → **23/23 pruebas unitarias OK**.
- La suite de integración **se omitió** (sin base de datos). El código está
  completo y listo para ejecutarse: instala PostgreSQL, crea `credit_cards_test`,
  corre `npm run migrate` y luego `NODE_ENV=test PGDATABASE=credit_cards_test npm test`.

## Limitaciones pendientes para un despliegue real

- Integrar autenticación y autorización.
- Sustituir la huella HMAC por tokenización de un proveedor de pagos certificado.
- Añadir una tabla `users` real y clave foránea para `user_id`.
- Rate limiting, observabilidad (logs estructurados, métricas) y auditoría.
- Revisión de cumplimiento PCI DSS según el alcance del manejo de tarjetas.
