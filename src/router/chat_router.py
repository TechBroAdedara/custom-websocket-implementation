from typing import Annotated, Sequence

from fastapi import WebSocket, APIRouter
from fastapi.params import Depends

from ..infra.websocket_pipeline import pipeline
from ..infra.websockets.chat_websocket_manager import ChatWebsocketManager
from ..schema.user_schema import UserOutModel
from ..schema.websocket_schema import ChatRoomDetails, ChatRoomMessageResponse
from ..services.chat_service import ChatService
from ..tools.utils import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat", "Websockets"])


@router.websocket("/")
async def initiate_websocket_connection(
    websocket: WebSocket, chat_websocket_manager: Annotated[ChatWebsocketManager, Depends()]
):
    await pipeline.persist_websocket_connection(
        websocket=websocket, websocket_manager=chat_websocket_manager
    )


@router.post("/rooms")
async def initiate_chat(
    chat_service: Annotated[ChatService, Depends()],
):
    """ This endpoint is to be called to create a chat room between a job poster and an applicant.
        It uses the application ID to initiate the chat room.
    """
    return await chat_service.initialize_chat_room()


@router.get("/rooms")
async def get_chat_rooms(
        chat_service: Annotated[ChatService, Depends()],
        user: Annotated[UserOutModel, Depends(get_current_user)],
) -> Sequence[ChatRoomDetails]:
    """This endpoint gets all chat rooms for a particular users."""
    return await chat_service.get_all_chat_rooms_for_user(user=user)


@router.get("/rooms/{room_id}")
async def get_chat_room_messages(
    room_id: str,
    chat_service: Annotated[ChatService, Depends()],
    user: Annotated[UserOutModel, Depends(get_current_user)],
) -> Sequence[ChatRoomMessageResponse]:
    """This endpoint gets all messsages that belong to a particular chat room"""
    return await chat_service.get_chat_room_messages(
        chat_room_id=room_id, user=user
    )



