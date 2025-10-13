from fastapi import APIRouter, Depends, WebSocket
from typing import Annotated

from ..infra.websockets.notification_websocket_manager import NotificationWebsocketManager
from ..infra.websocket_pipeline import pipeline

from ..schema.websocket_schema import NotificationWebsocketResponse, WebsocketMessageType, NotificationWebsocketType
from ..tools.logger import logger

router: APIRouter = APIRouter(prefix="/notification", tags=["Notifications"])

@router.websocket("/")
async def notification_websocket(
        websocket: WebSocket,
        notication_websocket_manager: Annotated[NotificationWebsocketManager, Depends()]
):
    logger.info("Notification websocket connected")
    await pipeline.persist_websocket_connection(
        websocket=websocket,
        websocket_manager=notication_websocket_manager
    )

@router.post("/user_id")
async def send_test_notification(
    user_id: str,
    notication_websocket_manager: Annotated[NotificationWebsocketManager, Depends()]
):
    test_notif: NotificationWebsocketResponse = NotificationWebsocketResponse(
        type=WebsocketMessageType.NOTIFICATION,
        content="This is a test notification",
        recipient_id=user_id,
        notification_type=NotificationWebsocketType.JOB
    )
    await notication_websocket_manager.send_text_to_websocket(recipient=user_id, message_data=test_notif)
