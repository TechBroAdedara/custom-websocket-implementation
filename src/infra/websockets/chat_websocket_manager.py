from typing import Annotated, Sequence

from fastapi.params import Depends
from starlette import status
from starlette.websockets import WebSocketDisconnect, WebSocket

from src.exceptions import NonExistentWebsocketRecipient, InvalidWebsocketMessage
from src.infra.websockets.base_websocket_manager import BaseWebsocketManager, WebsocketType
from src.schema.user_schema import UserOutModel
from src.schema.websocket_schema import WebsocketChatRequest, WebsocketChatResponse
from ..services.chat_service import ChatService
from src.tools.logger import logger

class ChatWebsocketManager(BaseWebsocketManager):
    websocket_type: WebsocketType = WebsocketType.CHAT

    def __init__(self, chat_service: Annotated[ChatService, Depends()]):
        self.chat_service: ChatService = chat_service
        super().__init__()

    async def listen(self, websocket: WebSocket):
        """Unique to this class that can listen to incoming messages and process them accordingly."""
        try:
            while True:
                try:
                    # RECIEVE
                    message: WebsocketChatRequest = await self.receive_text(websocket)
                    # PROCESS
                    stored_message: WebsocketChatResponse = (
                        await self.store_websocket_message(
                            message=message
                        )
                    )
                    await self.publish_message_to_chat_room(
                        message_data=stored_message
                    )
                except NonExistentWebsocketRecipient as e:
                    logger.warning(e)
                    await websocket.send_json({"error": str(e)})
                except InvalidWebsocketMessage as e:
                    logger.warning(e)
                    await websocket.close(
                        code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
                        reason=f"Invalid message format: {e}",
                    )
                    break
        except WebSocketDisconnect:
            logger.info("Client disconnected")
        except Exception as e:
            logger.exception(f"Unhandled exception in chat socket: {e}")

    async def store_websocket_message(self, message: WebsocketChatRequest):
        """Overridden to store chat messages in the database."""
        return await self.chat_service.add_message_to_chat_room(message)

    async def publish_message_to_chat_room(self, message_data: WebsocketChatResponse) -> None:
        """Overridden to publish chat messages to all the chat room participants/recipients."""
        room_id: str = message_data.chat_room_id
        room_participants: Sequence[UserOutModel] = await self.chat_service.get_chat_room_participants(room_id=room_id)
        room_participants_id: Sequence[str] = [p.user_id for p in room_participants]

        # We assume there will always be a user in a chatroom, as it is enforced by the business logic.
        # Therefore we do not need to check if the room participants list is empty
        for participant_id in room_participants_id:
            recipient = participant_id

            if recipient == message_data.sender_id:
                continue # Skip sending message to the sender

            await self.send_text_to_websocket(
                recipient=recipient,
                message_data=message_data,
            )
