from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.types import TokenType
from app.schemas import TokenData
from app.core.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def create_jwt(
    token_type, subject: str, expires_delta: Optional[timedelta] = None
) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif isinstance(expires_delta, int):
        expires_delta = timedelta(minutes=expires_delta)

    expire = datetime.utcnow() + expires_delta
    to_encode = {"token_type": token_type, "sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY)


async def _decode_token_base(token: str, expected_type: TokenType) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        token_type = payload.get("token_type")

        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Неправильный тип токена {token_type}. Ожидался {expected_type}",
            )
        return TokenData(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ошибка валидации токена: {str(e)}",
        )


async def decode_access_token(token: str) -> TokenData:
    return await _decode_token_base(token, TokenType.ACCESS)


async def decode_refresh_token(token: str) -> TokenData:
    return await _decode_token_base(token, TokenType.REFRESH)
