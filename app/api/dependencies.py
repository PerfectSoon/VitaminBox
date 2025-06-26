from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.connection import get_db

from app.core.security import decode_access_token, decode_refresh_token
from app.repositories import UserRepository
from app.schemas import TokenData
from app.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:

    return UserService(repository=UserRepository(db))


async def get_current_access_token(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    token_data = await decode_access_token(token)

    return token_data


async def get_current_refresh_token(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    token_data = await decode_refresh_token(token)

    return token_data
