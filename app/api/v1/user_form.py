from typing import List

from fastapi import APIRouter, HTTPException, Depends, status

from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    EntityNotFound,
)
from app.schemas import (
    GoalOut,
    GoalCreate,
    AllergyCreate,
    AllergyOut,
    UserOut,
    UserFormCreate,
    UserFormOut,
    UserFormUpdate,
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


@router.get(
    "/goals",
    response_model=List[GoalOut],
    summary="Получить все цели",
    responses={
        404: {"description": "Список целей пуст"},
        200: {"description": "Успешное получение списка целей"},
    },
)
async def get_all_goals(
    service: UserFormService = Depends(get_user_form_service),
) -> List[GoalOut]:
    try:
        return await service.get_goals()
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/allergies",
    response_model=List[AllergyOut],
    summary="Получить все аллергии",
    responses={
        404: {"description": "Список аллергий пуст"},
        200: {"description": "Успешное получение списка аллергий"},
    },
)
async def get_all_allergies(
    service: UserFormService = Depends(get_user_form_service),
) -> List[AllergyOut]:
    try:
        return await service.get_allergies()
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
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


@router.patch(
    "/form",
    response_model=UserFormOut,
    summary="Обновить анкету пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Анкета успешно обновлена"},
        404: {"description": "Анкета не найдена"},
        400: {"description": "Некорректные данные"},
        422: {"description": "Ошибка валидации данных"},
    },
)
async def update_user_form(
    form_update: UserFormUpdate,
    current_user: UserOut = Depends(get_current_user),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.update_user_form(current_user.id, form_update)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Указанные цели или аллергии не найдены: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные: {str(e)}",
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении анкеты: {str(e)}",
        )
