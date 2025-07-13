from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from app.api.dependencies import get_order_service, get_current_admin
from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    EntityNotFound,
    ServiceError,
)
from app.schemas import PromoOut, PromoCreate, UserOut
from app.services import OrderService

router = APIRouter()


@router.post(
    "/",
    response_model=PromoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый промокод",
    responses={
        400: {"description": "Некорректные данные"},
        409: {"description": "Промокод с таким именем уже существует"},
        500: {"description": "Ошибка сервера при создании промокода"},
    },
)
async def create_promo(
    promo_data: PromoCreate,
    admin: UserOut = Depends(get_current_admin),
    service: OrderService = Depends(get_order_service),
) -> PromoOut:
    try:
        return await service.promo_create(promo_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{promo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить промокод",
    responses={
        204: {"description": "Промокод успешно удален"},
        404: {"description": "Промокод не найден"},
        500: {"description": "Ошибка сервера при удалении промокода"},
    },
)
async def delete_promo(
    promo_id: int,
    admin: UserOut = Depends(get_current_admin),
    service: OrderService = Depends(get_order_service),
):
    try:
        await service.promo_delete(promo_id)
        return {"Deleted": "OK"}
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=List[PromoOut],
    summary="Получить все промокоды",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Список промокодов успешно получен"},
        404: {"description": "Список промокодов пуст"},
        500: {"description": "Ошибка сервера при получении промокодов"},
    },
)
async def get_all_promos(
    admin: UserOut = Depends(get_current_admin),
    service: OrderService = Depends(get_order_service),
) -> List[PromoOut]:

    try:
        return await service.get_all_promos()
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
