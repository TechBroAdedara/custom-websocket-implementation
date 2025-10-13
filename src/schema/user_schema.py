from pydantic import BaseModel
from typing import Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.user import User

class UserInModel(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str | None
    password: str | None = None
    profile_picture_url: Optional[str] = None
    signupoption: Optional[Literal["google", "email"]] = "email"
    privacy_preference: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "UserInModel":
        return cls(**data)

class UserOutModel(BaseModel):
    user_id: str
    firstname: str
    lastname: str
    email: str
    phone: str | None
    profile_picture_url: str | None

    @classmethod
    def from_user(cls, user_data: "User") -> "UserOutModel":
        return UserOutModel(
            user_id=user_data.id,
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            email=user_data.email,
            phone=user_data.phone,
            profile_picture_url=user_data.profile_picture_url,
        )