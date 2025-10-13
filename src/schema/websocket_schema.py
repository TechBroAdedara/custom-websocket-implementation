from datetime import datetime
from enum import StrEnum
from typing import Sequence
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from ..models.chat import ChatMessage
from .user_schema import UserOutModel

class ChatRoomMessageResponse(BaseModel):
    sender_id: str | None = None
    chat_room_id: str | None = None
    content: str
    created_at: datetime

    @classmethod
    def from_message(cls, chat: ChatMessage):
        return cls(
            sender_id=chat.sender_id,
            chat_room_id=chat.chat_room_id,
            content=chat.content,
            created_at=chat.created_at
        )

class ChatRoomDetails(BaseModel):
    chat_room_id: str
    participants: Sequence[UserOutModel] | None
    last_message: ChatRoomMessageResponse | None = None

class WebsocketMessageType(StrEnum):
    CHAT = "chat"
    NOTIFICATION = "notification"

class NotificationWebsocketType(StrEnum):
    JOB = "job"
    APPLICATION = "application"

class WebsocketChatRequest(BaseModel):
    sender_id: str
    recipient_id: str | None = None
    chat_room_id: str | None = None
    content: str
    type: WebsocketMessageType = WebsocketMessageType.CHAT
    created_at: datetime = datetime.now(tz=ZoneInfo("UTC"))

class BaseWebsocketResponse(BaseModel):
    type: WebsocketMessageType
    created_at: datetime = datetime.now(tz=ZoneInfo("UTC"))
    content: str

class WebsocketChatResponse(BaseWebsocketResponse):
    sender_id: str | None = None
    chat_room_id: str

class NotificationWebsocketResponse(BaseWebsocketResponse):
    recipient_id: str
    notification_type: NotificationWebsocketType
    additional_context: dict | None = None





