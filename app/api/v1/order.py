from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import OrderOut, OrderItemCreate
from app.services import OrderService
from app.api.dependencies import get_order_service, get_current_user
from app.schemas.user import UserOut
from app.exceptions.service_errors import EntityNotFound, ServiceError

router = APIRouter()


@router.get(
    "/cart",
    response_model=OrderOut,
    summary="Получить содержимое корзины пользователя",
    status_code=status.HTTP_200_OK,
)
async def get_cart(
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.get_active_cart(current_user.id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/",
    response_model=List[OrderOut],
    summary="Получить все заказы",
    responses={
        404: {"description": "Список заказов пуст"},
        200: {"description": "Успешное получение списка заказов"},
    },
)
async def get_all_orders(
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> List[OrderOut]:
    try:
        return await service.get_confirmed_cart(current_user.id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.post(
    "/cart/items",
    response_model=OrderOut,
    summary="Добавить товар в корзину",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    item: OrderItemCreate,
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.add_item_to_cart(current_user.id, item)
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/cart/items/{product_id}",
    response_model=OrderOut,
    summary="Удалить товар из корзины",
    status_code=status.HTTP_200_OK,
)
async def remove_from_cart(
    product_id: int,
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.remove_item_from_cart(current_user.id, product_id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.post(
    "/cart/apply-promo",
    response_model=OrderOut,
    summary="Применить промокод к корзине",
    status_code=status.HTTP_200_OK,
)
async def apply_promo_to_cart(
    promo: str = Query(..., description="Промокод"),
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.apply_promo_to_order(current_user.id, promo)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/cart/confirm",
    response_model=OrderOut,
    summary="Оформить заказ (подтвердить корзину)",
    status_code=status.HTTP_200_OK,
)
async def confirm_order(
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.confirm_order(current_user.id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/clear",
    response_model=OrderOut,
    summary="Очистить корзину",
    responses={
        200: {"description": "Корзина успешно очищена"},
        404: {"description": "Корзина не найдена"},
    },
)
async def clear_cart(
    current_user: UserOut = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.clear_cart(current_user.id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
