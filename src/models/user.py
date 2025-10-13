from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from src.tools.utils import generate_id

if TYPE_CHECKING:
    from .refresh_tokens import Token
    from .chat import ChatRoom


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=generate_id)
    firstname: Mapped[str] = mapped_column(String(64), nullable=False)
    lastname: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(20), nullable=True)
    state: Mapped[str] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(64), nullable=True)
    bio: Mapped[str] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    privacy_preference: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_picture_url: Mapped[str] = mapped_column(String(255), nullable=True)
    signupoption: Mapped[str] = mapped_column(String(15), nullable=False)

    tokens: Mapped["Token"] = relationship("Token", back_populates="user")
    chat_rooms: Mapped[list["ChatRoom"]] = relationship(
        "ChatRoom", secondary="chat_room_user", back_populates="users"
    )

    sent_messages = relationship(
        "ChatMessage", foreign_keys="[ChatMessage.sender_id]", back_populates="sender"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, firstname={self.firstname}, lastname={self.lastname}, email={self.email}, hashed_password={self.hashed_password}, phone={self.phone}, address_line1={self.address_line1}, address_line2={self.address_line2}, city={self.city}, state={self.state}, country={self.country}, bio={self.bio}, date_of_birth={self.date_of_birth}, privacy_preference={self.privacy_preference}, profile_picture_url={self.profile_picture_url}, signupoption={self.signupoption})>"
