from fastapi import APIRouter, HTTPException, Depends, status

from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
)
from app.schemas import (
    GoalOut,
    GoalCreate,
    AllergyCreate,
    AllergyOut,
    UserOut,
    UserFormCreate,
    UserFormOut,
)
from app.services import UserFormService

from app.api.dependencies import get_user_form_service, get_current_user

router = APIRouter()


@router.post(
    "/create/form",
    response_model=UserFormOut,
    summary="Создать анкету пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_form(
    user_form_in: UserFormCreate,
    current_user: UserOut = Depends(get_current_user),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.create_user_form(current_user.id, user_form_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/form",
    response_model=UserFormOut,
    summary="Просмотр анкеты пользователя",
    status_code=status.HTTP_200_OK,
)
async def get_user_form(
    current_user: UserOut = Depends(get_current_user),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        user_form = await service.get_user_form(current_user.id)
        return user_form
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.post(
    "/create/goal",
    response_model=GoalOut,
    summary="Создать цель",
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    goal_in: GoalCreate,
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.create_goal(goal_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/create/allergy",
    response_model=AllergyOut,
    summary="Создать аллергию",
    status_code=status.HTTP_201_CREATED,
)
async def create_allergy(
    allergy_in: AllergyCreate,
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.create_allergy(allergy_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/form",
    summary="Удаление анкеты пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_form(
    current_user: UserOut = Depends(get_current_user),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        await service.delete_user_form(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
