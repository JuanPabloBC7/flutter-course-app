"""Aplicación FastAPI que dispara notificaciones push vía FCM.

Endpoints:
- GET  /health                 -> healthcheck
- POST /notifications/order     -> push de orden a un usuario
- POST /notifications/broadcast -> push masivo a todos los usuarios

La documentación Swagger está disponible en /docs.
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import firebase_service
from models import (
    BroadcastNotificationRequest,
    BroadcastResponse,
    HealthResponse,
    NotificationResponse,
    OrderNotificationRequest,
)

# Cargar variables de entorno desde .env si existe
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la app: inicializa Firebase al arrancar."""
    # Inicializar Firebase Admin SDK antes de atender requests
    firebase_service.initialize_firebase()
    yield


app = FastAPI(
    title="BAM Wallet Notifications Backend",
    description="Backend para disparar notificaciones push vía Firebase Cloud Messaging.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS abierto para desarrollo local. Ajustar orígenes en producción.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Endpoint de salud para verificar que el servicio está arriba."""
    return HealthResponse(status="ok")


@app.post("/notifications/order", response_model=NotificationResponse)
def send_order_notification(
    request: OrderNotificationRequest,
) -> NotificationResponse:
    """Envía una notificación de orden al dispositivo del usuario.

    Busca el fcmToken del usuario en Firestore y envía la push.
    Retorna 404 si el usuario no tiene un fcmToken registrado.
    """
    # Buscar el token del usuario destino
    token = firebase_service.get_user_fcm_token(request.userId)
    if not token:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No se encontró un fcmToken para el usuario '{request.userId}'. "
                f"El usuario debe iniciar sesión en la app para registrar su token."
            ),
        )

    # Construir el cuerpo del mensaje con el formato solicitado
    body = f"Your order was placed! {request.itemCount} items - ${request.total}"

    try:
        # El data payload lleva el orderId para navegar al detalle en la app
        message_id = firebase_service.send_to_token(
            token=token,
            title="BAM Wallet",
            body=body,
            data={"orderId": request.orderId},
        )
    except Exception as exc:  # noqa: BLE001 - reportar cualquier fallo de FCM
        raise HTTPException(
            status_code=502,
            detail=f"Error al enviar la notificación vía FCM: {exc}",
        ) from exc

    return NotificationResponse(
        success=True,
        message="Notificación de orden enviada correctamente.",
        messageId=message_id,
    )


@app.post("/notifications/broadcast", response_model=BroadcastResponse)
def send_broadcast_notification(
    request: BroadcastNotificationRequest,
) -> BroadcastResponse:
    """Envía una notificación a todos los usuarios con fcmToken.

    Retorna 404 si no hay ningún usuario con token registrado.
    """
    # Recolectar todos los tokens disponibles
    tokens = firebase_service.get_all_fcm_tokens()
    if not tokens:
        raise HTTPException(
            status_code=404,
            detail="No hay usuarios con fcmToken registrado.",
        )

    try:
        success_count, failure_count = firebase_service.send_multicast(
            tokens=tokens,
            title=request.title,
            body=request.body,
        )
    except Exception as exc:  # noqa: BLE001 - reportar cualquier fallo de FCM
        raise HTTPException(
            status_code=502,
            detail=f"Error al enviar el broadcast vía FCM: {exc}",
        ) from exc

    return BroadcastResponse(
        success=True,
        message="Broadcast procesado.",
        totalTokens=len(tokens),
        successCount=success_count,
        failureCount=failure_count,
    )
