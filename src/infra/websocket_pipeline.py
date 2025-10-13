from fastapi import WebSocket
from starlette import status

from src.infra.websockets.base_websocket_manager import BaseWebsocketManager
from ..exceptions import (
    InvalidTokenError,
)
from ..infra.token import AccessToken
from ..schema.user_schema import UserOutModel
from ..tools import logger

async def authorize_websocket(websocket: WebSocket) -> WebSocket | None:
    token_header = websocket.headers.get("Authorization")
    access_token = token_header.split(" ")[1]

    try:
        authenticated_user: UserOutModel = await AccessToken.decode(token=access_token)
    except InvalidTokenError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token"
        )
        return None

    websocket.scope["user_id"] = authenticated_user.user_id
    return websocket


class WebsocketMessagePipeline:
    """
    Handles the management of websocket connections including authorization, maintaining
    connection state, and listening or sending keep-alive signals as necessary.

    Provides functionality to authorize websocket connections, manage their lifecycle
    through a websocket manager, and handle disconnection scenarios. This class
    supports any websocket manager that complies with the BaseWebsocketManager interface
    and can optionally handle managers with listenable capabilities.
    """

    async def persist_websocket_connection(
            self,
            websocket: WebSocket,
            websocket_manager: BaseWebsocketManager
    ) -> None:
        authenticated_websocket = await authorize_websocket(websocket=websocket)
        if not authenticated_websocket:
            return None

        websocket = await websocket_manager.accept_websocket(websocket=authenticated_websocket)
        await websocket_manager.listen(websocket=websocket)

        await websocket_manager.disconnect_websocket(websocket)
        logger.warning(f"Disconnected socket for user: {websocket.scope["user_id"]} upon exception")
        return None


pipeline = WebsocketMessagePipeline()
