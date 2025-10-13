import string
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pynanoid import generate

from src.infra.token import AccessToken
from src.schema.user_schema import UserOutModel

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def generate_id():
    alphabet = string.ascii_letters + string.digits
    return generate(alphabet=alphabet, size=10)

async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
) -> UserOutModel:
    """
    Gets its token parameter from a FastAPI Dependency that checks the request for an "Authorization" header
    :param token:
    :return: user_data: str
    """
    payload: UserOutModel = await AccessToken.decode(token)
    return payload
