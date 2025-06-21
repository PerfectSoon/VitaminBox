from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.connection import get_db

from app.core.security import decode_access_token
from app.repositories import UserRepository
from app.schemas import UserOut
from app.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserOut:
    token_data = decode_access_token(token)
    user_service = UserService(repository=UserRepository(db=db))

    user = await user_service.get_user(int(token_data.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:

    return UserService(repository=UserRepository(db))
