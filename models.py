"""Modelos Pydantic para validación de requests y responses del backend."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class OrderNotificationRequest(BaseModel):
    """Payload para disparar una notificación de orden de compra."""

    # ID del usuario (coincide con el campo `userId` en Firestore)
    userId: str = Field(..., min_length=1, description="ID del usuario destino")
    # ID de la orden, se envía en el data payload para navegar al detalle
    orderId: str = Field(..., min_length=1, description="ID de la orden")
    # Total de la orden; se recibe como string para preservar el formato
    total: str = Field(..., description="Total de la orden (ej. '49.99')")
    # Cantidad de items en la orden
    itemCount: int = Field(..., ge=0, description="Cantidad de items")


class BroadcastNotificationRequest(BaseModel):
    """Payload para enviar una notificación a todos los usuarios."""

    # Título de la notificación
    title: str = Field(..., min_length=1, description="Título de la notificación")
    # Cuerpo de la notificación
    body: str = Field(..., min_length=1, description="Cuerpo de la notificación")


class NotificationResponse(BaseModel):
    """Respuesta estándar para un envío individual."""

    success: bool
    message: str
    # ID del mensaje devuelto por FCM cuando el envío es exitoso
    messageId: Optional[str] = None


class BroadcastResponse(BaseModel):
    """Respuesta para el envío masivo con conteo de éxitos y fallos."""

    success: bool
    message: str
    # Cantidad de dispositivos a los que se intentó enviar
    totalTokens: int
    # Cantidad de envíos exitosos
    successCount: int
    # Cantidad de envíos fallidos
    failureCount: int


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: str
