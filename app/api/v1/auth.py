from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status

from app.core.exceptions import (
    UserAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.core.security import create_jwt
from app.core.settings import settings
from app.core.types import TokenType

from app.services import UserService
from app.schemas import (
    UserOut,
    UserAuth,
    UserCreate,
    Token,
    TokenData,
)
from app.api.dependencies import (
    get_current_access_token,
    get_user_service,
    get_current_refresh_token,
)

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register_owner(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    try:
        return await service.register(user_in)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    try:
        auth_user = await service.authenticate(
            UserAuth(email=form_data.username, password=form_data.password)
        )
    except (UserNotFoundError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_jwt(
        token_type=TokenType.ACCESS,
        subject=str(auth_user.id),
    )
    refresh_token = await create_jwt(
        token_type=TokenType.REFRESH,
        subject=str(auth_user.id),
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserOut)
async def read_profile(
    token_data: TokenData = Depends(get_current_access_token),
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.get_user(int(token_data.sub))
        return UserOut.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str("Пользователь не авторизован"),
        )


@router.get("/profile/{user_id}", response_model=UserOut)
async def read_profile_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_data: TokenData = Depends(get_current_refresh_token),
):

    new_access_token = await create_jwt(
        token_type=TokenType.ACCESS,
        subject=token_data.sub,
    )
    new_refresh_token = await create_jwt(
        token_type=TokenType.REFRESH,
        subject=token_data.sub,
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
