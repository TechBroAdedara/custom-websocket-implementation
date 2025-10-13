from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.chat import ChatRoom, User, ChatRoomUser, ChatMessage
from ..schema.user_schema import UserOutModel
from ..schema.websocket_schema import WebsocketChatRequest


class ChatRepository:
    @classmethod
    async def create_chat_room(cls, conn: AsyncSession) -> ChatRoom:
        chat_room: ChatRoom = ChatRoom()

        conn.add(chat_room)
        await conn.flush()
        await conn.refresh(chat_room)

        return chat_room

    @classmethod
    async def get_chat_room_by_id(
        cls, conn: AsyncSession, chat_room_id: str
    ) -> ChatRoom | None:
        stmt = (
            select(ChatRoom)
            .where(ChatRoom.id == chat_room_id)
            .options(selectinload(ChatRoom.users))
        )
        result = await conn.execute(stmt)
        chat_room = result.scalar_one_or_none()
        return chat_room

    @classmethod
    async def add_user_to_chat_room(
        cls, chat_room: ChatRoom, user: User, conn: AsyncSession
    ) -> ChatRoomUser:
        chat_room_user = ChatRoomUser(
            chat_room_id=chat_room.id,
            user_id=user.id,
        )

        conn.add(chat_room_user)
        await conn.flush()
        await conn.refresh(chat_room)

        return chat_room_user

    @classmethod
    async def add_message_to_chat_room(
        cls, chat_room: ChatRoom, message: WebsocketChatRequest, conn: AsyncSession
    ) -> ChatMessage:
        chat_message = ChatMessage(
            sender_id=message.sender_id,
            chat_room_id=chat_room.id,
            content=message.content,
        )

        conn.add(chat_message)
        await conn.flush()
        await conn.refresh(chat_room)

        return chat_message

    @classmethod
    async def get_users_in_chat_room(
        cls, conn: AsyncSession, chat_room_id: str
    ) -> list[User] | None:
        stmt = (
            select(ChatRoom)
            .where(ChatRoom.id == chat_room_id)
            .options(selectinload(ChatRoom.users))
        )
        result = await conn.execute(stmt)
        chat_room = result.scalar_one_or_none()

        if not chat_room:
            return None

        return chat_room.users

    @classmethod
    async def get_messages_from_chat_room(
        cls, conn: AsyncSession, chat_room_id: str
    ) -> Sequence[ChatMessage] | None:
        stmt = select(ChatMessage).where(ChatMessage.chat_room_id == chat_room_id)
        result = await conn.execute(stmt)
        chat_messages = result.scalars().all()

        return chat_messages

    @classmethod
    async def get_all_chat_rooms_for_user(cls, conn: AsyncSession, user: UserOutModel):
        stmt = (
            select(ChatRoom)
            .join(ChatRoomUser, ChatRoomUser.chat_room_id == ChatRoom.id)
            .where(ChatRoomUser.user_id == user.user_id)
            .options(
                selectinload(ChatRoom.users)
            )
        )
        result = await conn.execute(stmt)
        return result.scalars().all()
