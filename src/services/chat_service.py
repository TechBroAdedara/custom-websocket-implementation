from typing import Annotated, Sequence

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from ..db import get_db_session
from ..exceptions import NonExistentWebsocketRecipient, InvalidWebsocketAction
from ..models.chat import ChatRoom, User, ChatMessage
from ..repositories.user_repository import UserRepository
from ..repositories.chat_repository import ChatRepository
from ..schema.user_schema import UserOutModel
from ..schema.websocket_schema import WebsocketChatResponse, ChatRoomDetails, ChatRoomMessageResponse, \
    WebsocketChatRequest, WebsocketMessageType
from ..tools.logger import logger


class ChatService:
    def __init__(
        self,
        chat_repo: Annotated[ChatRepository, Depends()],
        user_repo: Annotated[UserRepository, Depends()],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ):
        self.chat_repo = chat_repo
        self.user_repo = user_repo
        self.session = session

    async def initialize_chat_room(
        self
    ) -> ChatRoom:
        async with self.session.begin():
            chat_room: ChatRoom = await self.chat_repo.create_chat_room(
                conn=self.session
            )

            return chat_room

    async def add_user_to_chat_room(self, user_id: str):
        raise NotImplementedError

    async def is_user_in_chat_room(self, user_id: str, chat_room_id: str):
        chat_room_users: list[User] = await self.chat_repo.get_users_in_chat_room(
            conn=self.session, chat_room_id=chat_room_id
        )

        chat_room_user_ids = [user.id for user in chat_room_users]
        if user_id not in chat_room_user_ids:
            return False
        else:
            return True

    async def add_message_to_chat_room(
        self, message: WebsocketChatRequest
    ) -> WebsocketChatResponse:
        async with self.session.begin():
            if message.type != WebsocketMessageType.CHAT:
                raise InvalidWebsocketAction("You cannot send this message type to a chat room")

            chat_room: ChatRoom = await self.chat_repo.get_chat_room_by_id(
                conn=self.session, chat_room_id=message.chat_room_id
            )
            if not chat_room:
                raise NonExistentWebsocketRecipient("Chat room not found")

            chat_room_message: ChatMessage = (
                await self.chat_repo.add_message_to_chat_room(
                    chat_room=chat_room, message=message, conn=self.session
                )
            )

            logger.info(f"Added message to chat room: {chat_room_message.content}")

            return WebsocketChatResponse(
                sender_id=chat_room_message.sender_id,
                chat_room_id=chat_room_message.chat_room_id,
                content=chat_room_message.content,
                created_at=chat_room_message.created_at,
                type=message.type,
            )

    async def get_chat_room_messages(self, chat_room_id: str, user: UserOutModel) -> Sequence[ChatRoomMessageResponse]:
        if not await self.is_user_in_chat_room(
            user_id=user.user_id, chat_room_id=chat_room_id
        ):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="You cannot view this chat room"
            )

        messages: Sequence[
            ChatRoomMessageResponse
        ] = [
                ChatRoomMessageResponse.from_message(chat)
                for chat in
                await self.chat_repo.get_messages_from_chat_room(
                    conn=self.session, chat_room_id=chat_room_id
                    )
            ]
        return messages

    async def get_all_chat_rooms_for_user(self, user: UserOutModel) -> Sequence[ChatRoomDetails]:
        chat_rooms: Sequence[ChatRoom] =  await self.chat_repo.get_all_chat_rooms_for_user(
            conn=self.session, user=user
        )

        chat_room_users: dict[str, Sequence[UserOutModel]] = {
            chat_room.id: [UserOutModel.from_user(user) for user in chat_room.users]
            for chat_room in chat_rooms
        }

        chat_room_messages: dict[str, Sequence[ChatRoomMessageResponse]] = {
            chat_room.id: await self.get_chat_room_messages(chat_room.id, user=user)
            for chat_room in chat_rooms
        }
        return [
            ChatRoomDetails(
                chat_room_id=chat_room.id,
                participants=chat_room_users[chat_room.id],
                last_message=chat_room_messages[chat_room.id][-1]
            )
            for chat_room in chat_rooms
        ]

    async def get_chat_room_participants(self, room_id: str):
        async with self.session.begin():
            chat_room: ChatRoom = await self.chat_repo.get_chat_room_by_id(
                conn=self.session,
                chat_room_id=room_id
            )

            if not chat_room:
                raise NonExistentWebsocketRecipient("Chat room not found")


            users: Sequence[User] = chat_room.users
            return [UserOutModel.from_user(user) for user in users]






