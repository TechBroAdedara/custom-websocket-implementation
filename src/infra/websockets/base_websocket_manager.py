from abc import ABC, abstractmethod
from collections import defaultdict
from enum import StrEnum
from json import JSONDecodeError
from typing import Protocol, runtime_checkable, DefaultDict

from pydantic import ValidationError
from starlette.websockets import WebSocket

from src.exceptions import NonExistentWebsocketRecipient, InvalidWebsocketMessage
from src.schema.websocket_schema import WebsocketChatRequest, WebsocketChatResponse, WebsocketMessageType, \
    BaseWebsocketResponse
from src.tools.logger import logger


class WebsocketType(StrEnum):
    CHAT = "chat"
    NOTIFICATION = "notification"

    @property
    def websocket_store(self) -> DefaultDict[str, list[WebSocket]]:
        return WEBSOCKET_STORE[self]


# Will switch to redis pub/sub system soon
WEBSOCKET_STORE: dict[
    str, DefaultDict[
        str, list[WebSocket]
    ]
] = {
    WebsocketType.CHAT: defaultdict(list),
    WebsocketType.NOTIFICATION: defaultdict(list)
}


class BaseWebsocketManager(ABC):
    """
    Defines a base class for managing websocket communication, including accepting, disconnecting, and communicating
    via websockets. This class provides an abstract method for storing websocket messages and various utility methods
    to handle websocket operations.
    """
    websocket_type: WebsocketType

    @abstractmethod
    async def store_websocket_message(self, *args, **kwargs): ...

    @abstractmethod
    async def listen(self, *args, **kwargs): ...

    @classmethod
    async def accept_websocket(cls, websocket: WebSocket):
        """
        Accepts a websocket connection, thereby upgrading the connection to a websocket protocol.
        Appends the websocket object to the list of active websockets.
        """
        await websocket.accept()
        cls.websocket_type.websocket_store[websocket.scope["user_id"]].append(websocket)
        logger.info(f"Active websocket connections: {len(cls.websocket_type.websocket_store)}")

        return websocket

    @classmethod
    async def disconnect_websocket(cls, websocket: WebSocket):

        """
        Deletes the websocket from the list of active websockets. Subsequently closes the websocket connection
        """
        user_id = websocket.scope.get("user_id")
        if not user_id:
            return

        sockets = cls.websocket_type.websocket_store.get(user_id, [])
        if websocket in sockets:
            sockets.remove(websocket)

        # Clean up empty lists to avoid memory growth
        if not sockets:
            cls.websocket_type.websocket_store.pop(user_id, None)

        try:
            await websocket.close()
        except RuntimeError:
            logger.warning("Failed to close websocket connection: It seems the connection was already closed.")

    @classmethod
    async def send_text_to_websocket(cls, recipient: str, message_data: BaseWebsocketResponse) -> None:
        """ Gets all the websockets for a recipient and uses a loop to send a message to them"""
        sockets: list[WebSocket] = cls.websocket_type.websocket_store.get(recipient)

        if not sockets:
            raise NonExistentWebsocketRecipient("Recipient websocket does not exist yet")

        for socket in sockets:
            await socket.send_text(message_data.model_dump_json())

    @classmethod
    async def publish_message_to_all_sockets(cls, message_data: WebsocketChatResponse) -> None:
        """ Sends a system wide notification to all the notification websockets"""
        if cls.websocket_type is WebsocketType.NOTIFICATION:
            """ Only send broadcast message to notification websockets"""
            for recipient in cls.websocket_type.websocket_store:
                await cls.send_text_to_websocket(
                    recipient=recipient,
                    message_data=message_data,
                )

    @staticmethod
    async def parse_websocket_message(websocket_message: dict) -> WebsocketChatRequest:
        """
        Validates the structure of the websocket message with the WebsocketMesssageRequest object
        and returns the parsed message.
        """
        try:
            message: WebsocketChatRequest = WebsocketChatRequest.model_validate(websocket_message)
        except ValidationError as e:
            logger.info(f"Failed to parse websocket data: {e}")
            raise InvalidWebsocketMessage("Invalid websocket message format")
        except JSONDecodeError as e:
            logger.info(f"Failed to parse websocket data: {e}")
            raise InvalidWebsocketMessage("Invalid JSON format")

        return message

    @staticmethod
    def _check_message_type(message: WebsocketChatRequest) -> None:
        if message.type not in list(WebsocketMessageType):
            raise InvalidWebsocketMessage("Invalid message type")

    async def receive_text(self, websocket: WebSocket) -> WebsocketChatRequest:
        """Receives text from a websocket connection, parses and validates it, and returns a WebsocketMessageRequest object."""
        message_dict: dict = await websocket.receive_json()
        message: WebsocketChatRequest = await self.parse_websocket_message(websocket_message=message_dict)
        self._check_message_type(message=message)

        if websocket.scope["user_id"] != message.sender_id:
            logger.info("Websocket's userID scope does not match message sender_id")
            raise InvalidWebsocketMessage("Websocket is malformed or corrupted")

        return message
