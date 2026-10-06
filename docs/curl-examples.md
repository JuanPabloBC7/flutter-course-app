# Ejemplos de cURL

Base: `http://localhost:4000/api/v1`. Ajusta el puerto según tu `.env`.

> Los números de tarjeta son **sintéticos** y Luhn-válidos, solo para pruebas.
> No uses tarjetas reales.

Variable de ayuda:

```bash
BASE=http://localhost:4000/api/v1
```

---

## API 3 — Crear tarjeta (POST) — caso exitoso

```bash
curl -i -X POST "$BASE/credit-cards" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "cardNumber": "4111 1111 1111 1111",
    "expirationMonth": 12,
    "expirationYear": 2030,
    "cvv": "123",
    "creditLimit": 5000.00
  }'
# 201 Created
# { "data": { "id": "...", "userId": "user-123", "brand": "VISA",
#             "last4": "1111", "creditLimit": "5000.00", "status": "ACTIVE",
#             "expirationMonth": 12, "expirationYear": 2030, ... } }
```

### Crear — error: falta userId (400)

```bash
curl -i -X POST "$BASE/credit-cards" \
  -H "Content-Type: application/json" \
  -d '{ "cardNumber": "4111111111111111", "expirationMonth": 12,
        "expirationYear": 2030, "cvv": "123", "creditLimit": 5000 }'
# 400 Bad Request -> error.code = VALIDATION_ERROR
```

### Crear — error: checksum de Luhn inválido (400)

```bash
curl -i -X POST "$BASE/credit-cards" \
  -H "Content-Type: application/json" \
  -d '{ "userId": "user-123", "cardNumber": "4111111111111112",
        "expirationMonth": 12, "expirationYear": 2030, "cvv": "123",
        "creditLimit": 5000 }'
# 400 Bad Request
```

### Crear — Mastercard (rango 2221–2720)

```bash
curl -i -X POST "$BASE/credit-cards" \
  -H "Content-Type: application/json" \
  -d '{ "userId": "user-456", "cardNumber": "2221000000000009",
        "expirationMonth": 6, "expirationYear": 2029, "cvv": "321",
        "creditLimit": 3000 }'
# 201 Created -> data.brand = "MASTERCARD"
```

---

## API 1 — Listar tarjetas activas (GET)

```bash
curl -i "$BASE/credit-cards"
# 200 OK -> { "data": [ ... ] }   (array vacío si no hay tarjetas)
```

---

## API 5 — Obtener una tarjeta por id (GET)

Sustituye `<ID>` por el id devuelto al crear.

```bash
curl -i "$BASE/credit-cards/<ID>"
# 200 OK -> { "data": { ... } }
```

### Obtener — no existe (404)

```bash
curl -i "$BASE/credit-cards/550e8400-e29b-41d4-a716-446655440000"
# 404 Not Found -> error.code = NOT_FOUND
```

### Obtener — id con formato inválido (400)

```bash
curl -i "$BASE/credit-cards/not-a-uuid"
# 400 Bad Request -> error.code = VALIDATION_ERROR
```

---

## API 2 — Actualizar tarjeta (PATCH)

```bash
curl -i -X PATCH "$BASE/credit-cards/<ID>" \
  -H "Content-Type: application/json" \
  -d '{ "creditLimit": 7500.00, "status": "ACTIVE" }'
# 200 OK -> { "data": { ..., "creditLimit": "7500.00" } }
```

### Actualizar solo un campo

```bash
curl -i -X PATCH "$BASE/credit-cards/<ID>" \
  -H "Content-Type: application/json" \
  -d '{ "status": "BLOCKED" }'
# 200 OK
```

### Actualizar — cuerpo vacío (400)

```bash
curl -i -X PATCH "$BASE/credit-cards/<ID>" \
  -H "Content-Type: application/json" \
  -d '{}'
# 400 Bad Request
```

### Actualizar — campo no permitido (400)

```bash
curl -i -X PATCH "$BASE/credit-cards/<ID>" \
  -H "Content-Type: application/json" \
  -d '{ "userId": "otro" }'
# 400 Bad Request (strict: solo creditLimit y status)
```

### Actualizar — valor inválido (400)

```bash
curl -i -X PATCH "$BASE/credit-cards/<ID>" \
  -H "Content-Type: application/json" \
  -d '{ "creditLimit": -1 }'
# 400 Bad Request
```

### Actualizar — tarjeta inexistente (404)

```bash
curl -i -X PATCH "$BASE/credit-cards/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{ "status": "ACTIVE" }'
# 404 Not Found
```

---

## API 4 — Eliminar tarjeta (DELETE, soft delete)

```bash
curl -i -X DELETE "$BASE/credit-cards/<ID>"
# 204 No Content (sin cuerpo)
```

### Eliminar — ya eliminada o inexistente (404)

```bash
curl -i -X DELETE "$BASE/credit-cards/<ID>"
# 404 Not Found (al repetir sobre una ya eliminada)
```

### Verificar que no reaparece

```bash
curl -i "$BASE/credit-cards/<ID>"      # 404
curl -i "$BASE/credit-cards"           # no incluye la tarjeta eliminada
```
