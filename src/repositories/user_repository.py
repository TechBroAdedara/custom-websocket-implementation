from sqlalchemy import select, update, Result, Select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..schema.user_schema import UserInModel


class UserRepository:
    def __init__(self):
        self.table = User

    async def create_new_user(self, conn: AsyncSession, new_user: UserInModel) -> User:
        """
        Creates a new user resource in the database.
        :param conn:
        :param new_user: New user model
        :return: created user
        """
        user: User = self.table(
            firstname=new_user.firstname,
            lastname=new_user.lastname,
            email=new_user.email,
            phone=new_user.phone,
            hashed_password=new_user.password,
            signupoption=new_user.signupoption,
            profile_picture_url=new_user.profile_picture_url,
            privacy_preference=new_user.privacy_preference,
        )

        conn.add(user)
        await conn.flush()
        await conn.refresh(user)

        return user

    async def get_user_by_id(self, conn: AsyncSession, user_id: str) -> User | None:
        stmt: Select = select(self.table).where(User.id == user_id)
        result: Result = await conn.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, conn: AsyncSession, email: str) -> User:
        """
        Gets user from database with email

        :param conn:
        :param email: Email of user to fetch
        :return: user
        """
        stmt: Select = select(self.table).where(User.email == email)
        result: Result["User"] = await conn.execute(stmt)

        user: User = result.scalar_one_or_none()
        return user

    async def update_user_details(
        self, conn: AsyncSession, user_id: str, user_details: dict
    ) -> User:
        stmt = (
            update(self.table)
            .where(User.id == user_id)
            .values(**user_details)
            .execution_options(synchronize_session="fetch")
        )
        result = await conn.execute(stmt)
        await conn.flush()
        user = result.scalar_one_or_none()

        return user
