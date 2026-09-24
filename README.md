# flutter_course_backend

Backend en **FastAPI** que dispara notificaciones push vía **Firebase Cloud Messaging (FCM)**
usando el **Firebase Admin SDK**. Pensado para la app Flutter *BAM Wallet*
(Firebase project `flutter-course-85e95`).

## Estructura

```
flutter_course_backend/
├── main.py              # App FastAPI + endpoints
├── firebase_service.py  # Lógica de Firestore + envío FCM (Admin SDK)
├── models.py            # Modelos Pydantic (request/response)
├── requirements.txt     # Dependencias
├── .env.example         # Variables de entorno de ejemplo
├── .gitignore           # Excluye serviceAccountKey.json y venv
└── README.md
```

## Endpoints

| Método | Ruta                      | Descripción                                        |
|--------|---------------------------|----------------------------------------------------|
| GET    | `/health`                 | Healthcheck. Retorna `{ "status": "ok" }`.         |
| POST   | `/notifications/order`    | Push de orden a un usuario (busca su `fcmToken`).  |
| POST   | `/notifications/broadcast`| Push masivo a todos los usuarios con `fcmToken`.   |

Documentación interactiva (Swagger): http://localhost:8000/docs

## Setup

### 1. Crear y activar el entorno virtual

```bash
cd flutter_course_backend
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
# En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Colocar el serviceAccountKey.json

1. En la consola de Firebase, ve a **Project Settings → Service accounts**.
2. Genera una nueva clave privada (**Generate new private key**).
3. Guarda el archivo descargado como `serviceAccountKey.json` en la **raíz del backend**
   (`flutter_course_backend/serviceAccountKey.json`).

> Este archivo contiene credenciales sensibles y ya está en `.gitignore`.
> Si prefieres otra ruta, define `SERVICE_ACCOUNT_KEY_PATH` en un archivo `.env`
> (usa `.env.example` como plantilla).

### 4. (Opcional) Variables de entorno

```bash
cp .env.example .env
```

## Correr el servidor local

```bash
uvicorn main:app --reload --port 8000
```

El servidor quedará en http://localhost:8000 y Swagger en http://localhost:8000/docs.

## Probar los endpoints

### Health

```bash
curl http://localhost:8000/health
# -> {"status":"ok"}
```

### Notificación de orden

Requiere que el usuario ya haya iniciado sesión en la app (para que exista su `fcmToken`
en Firestore). El `userId` debe coincidir con el campo `userId` del documento en `users`.

```bash
curl -X POST http://localhost:8000/notifications/order \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "UID_DEL_USUARIO",
    "orderId": "ORDER_123",
    "total": "49.99",
    "itemCount": 3
  }'
```

Respuesta esperada:

```json
{
  "success": true,
  "message": "Notificación de orden enviada correctamente.",
  "messageId": "projects/flutter-course-85e95/messages/..."
}
```

Si el usuario no tiene `fcmToken`, responde `404`.

### Broadcast

```bash
curl -X POST http://localhost:8000/notifications/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "title": "BAM Wallet",
    "body": "Nueva promoción disponible"
  }'
```

Respuesta esperada:

```json
{
  "success": true,
  "message": "Broadcast procesado.",
  "totalTokens": 2,
  "successCount": 2,
  "failureCount": 0
}
```

También puedes probar todo desde Swagger en `/docs` con el botón **Try it out**.
