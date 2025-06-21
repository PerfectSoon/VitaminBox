from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status

from app.core.exceptions import (
    UserAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.core.security import create_access_token
from app.database.models import User
from app.services import UserService
from app.schemas import (
    UserOut,
    UserAuth,
    UserCreate,
    Token,
)
from app.api.dependencies import get_current_user, get_user_service

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

    access_token = create_access_token(
        subject=str(auth_user.id),
        role=auth_user.role.value,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=auth_user.role.value,
    )


@router.get("/profile", response_model=UserOut)
async def read_profile(
    current_user: User = Depends(get_current_user),
):
    return UserOut.model_validate(current_user)


@router.get("/profile/{user_id}", response_model=UserOut)
async def read_profile_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
