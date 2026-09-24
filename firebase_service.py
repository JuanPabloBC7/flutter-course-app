"""Servicio de integración con Firebase Admin SDK.

Responsabilidades:
- Inicializar el Admin SDK a partir de un archivo serviceAccountKey.json
- Consultar los FCM tokens de los usuarios en Firestore
- Enviar notificaciones push vía Firebase Cloud Messaging (FCM)
"""

from __future__ import annotations

import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, messaging

# Ruta al archivo de credenciales del service account.
# Se puede sobreescribir con la variable de entorno SERVICE_ACCOUNT_KEY_PATH.
SERVICE_ACCOUNT_KEY_PATH = os.getenv(
    "SERVICE_ACCOUNT_KEY_PATH", "serviceAccountKey.json"
)

# Nombre de la colección de usuarios en Firestore.
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

# Cliente de Firestore (se inicializa en initialize_firebase()).
_db: Optional[firestore.Client] = None


def initialize_firebase() -> None:
    """Inicializa el Admin SDK y el cliente de Firestore.

    Debe llamarse una sola vez durante el arranque de la aplicación.
    Lanza FileNotFoundError si no existe el archivo de credenciales.
    """
    global _db

    # Evitar doble inicialización si ya existe una app por defecto
    if not firebase_admin._apps:
        if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
            raise FileNotFoundError(
                f"No se encontró el archivo de credenciales en "
                f"'{SERVICE_ACCOUNT_KEY_PATH}'. Colócalo en la raíz del backend "
                f"o define SERVICE_ACCOUNT_KEY_PATH."
            )
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()


def _get_db() -> firestore.Client:
    """Devuelve el cliente de Firestore o lanza error si no está listo."""
    if _db is None:
        raise RuntimeError(
            "Firebase no ha sido inicializado. Llama a initialize_firebase() primero."
        )
    return _db


def get_user_fcm_token(user_id: str) -> str | None:
    """Obtiene el fcmToken del usuario cuyo campo `userId` coincide.

    El documento se identifica por el campo `userId` (no por el ID del
    documento), por eso se usa una query en lugar de un get directo.

    Retorna el token o None si el usuario no existe o no tiene token.
    """
    db = _get_db()

    query = (
        db.collection(USERS_COLLECTION)
        .where("userId", "==", user_id)
        .limit(1)
        .stream()
    )

    for doc in query:
        data = doc.to_dict() or {}
        token = data.get("fcmToken")
        # Ignorar tokens vacíos o inexistentes
        if token:
            return token
        return None

    return None


def get_all_fcm_tokens() -> list[str]:
    """Obtiene todos los fcmToken no vacíos de la colección de usuarios."""
    db = _get_db()

    tokens: list[str] = []
    for doc in db.collection(USERS_COLLECTION).stream():
        data = doc.to_dict() or {}
        token = data.get("fcmToken")
        if token:
            tokens.append(token)

    return tokens


def send_to_token(
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> str:
    """Envía una notificación push a un dispositivo específico.

    Retorna el messageId devuelto por FCM.
    Lanza excepción si el envío falla (ej. token inválido).
    """
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        # El data payload debe tener valores string
        data=data or {},
        token=token,
    )
    return messaging.send(message)


def send_multicast(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> tuple[int, int]:
    """Envía una notificación push a múltiples dispositivos.

    Retorna una tupla (successCount, failureCount).
    Los fallos individuales (tokens inválidos) no interrumpen el envío.
    """
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
        tokens=tokens,
    )
    # send_each_for_multicast maneja cada token de forma independiente
    response = messaging.send_each_for_multicast(message)
    return response.success_count, response.failure_count
