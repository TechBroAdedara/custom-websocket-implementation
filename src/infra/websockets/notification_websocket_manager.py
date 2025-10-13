import asyncio

from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.infra.websockets.base_websocket_manager import WebsocketType
from src.exceptions import NonExistentWebsocketRecipient, InvalidWebsocketMessage
from src.infra.websockets.base_websocket_manager import BaseWebsocketManager
from src.schema.websocket_schema import NotificationWebsocketResponse
from src.tools.logger import logger

class NotificationWebsocketManager(BaseWebsocketManager):
    websocket_type: WebsocketType = WebsocketType.NOTIFICATION

    async def store_websocket_message(self, message: NotificationWebsocketResponse):
        """To be implemented"""
        raise NotImplementedError("Not Implemented yet")

    async def listen(self, websocket: WebSocket):
        try:
            while True:
                try:
                    await asyncio.sleep(30)
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