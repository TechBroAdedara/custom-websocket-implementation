from datetime import datetime
from typing import Optional, TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, TEXT, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.tools.utils import generate_id
from ..db import Base

if TYPE_CHECKING:
    from .user import User


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_id)
    sender_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    chat_room_id: Mapped[str] = mapped_column(
        ForeignKey("chat_room.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(tz=ZoneInfo("UTC")),
    )

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    chat_room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")


class ChatRoomUser(Base):
    __tablename__ = "chat_room_user"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_id)
    chat_room_id: Mapped[str] = mapped_column(
        ForeignKey("chat_room.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )

    # user: Mapped["User"] = relationship("User", back_populates="chat_rooms")


class ChatRoom(Base):
    __tablename__ = "chat_room"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_id)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(tz=ZoneInfo("UTC")),
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="chat_room"
    )
    users: Mapped[list["User"]] = relationship(
        "User", secondary="chat_room_user", back_populates="chat_rooms"
    )

    def get_recipient_for(self, sender_id: str) -> str | None:
        """Return the ID of the other user in this two-person chat."""
        for user in self.users:
            if user.id != sender_id:
                return user.id
        return None
