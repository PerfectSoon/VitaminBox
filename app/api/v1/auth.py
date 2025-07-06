from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks

from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.core.security import create_jwt
from app.core.settings import settings
from app.core.types import TokenType

from app.services import UserService, NotificationService
from app.schemas import (
    UserOut,
    UserAuth,
    UserCreate,
    Token,
    TokenData,
)
from app.api.dependencies import (
    get_user_service,
    get_current_refresh_token,
    get_current_user,
    get_notification_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=UserOut,
    summary="Регистрация нового пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    background_tasks: BackgroundTasks,
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    try:
        user = await service.register(user_in)
        background_tasks.add_task(
            notification_service.send_reg_email, user.email, user
        )

        return user
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Авторизация и получение JWT токенов",
    status_code=status.HTTP_200_OK,
)
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


@router.get(
    "/me",
    response_model=UserOut,
    summary="Получить данные текущего авторизованного пользователя",
    status_code=status.HTTP_200_OK,
)
async def read_profile(
    current_user: UserOut = Depends(get_current_user),
):
    try:
        return current_user
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str("Пользователь не авторизован или токен не действителен"),
        )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление пары access и refresh токенов",
    status_code=status.HTTP_200_OK,
)
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
