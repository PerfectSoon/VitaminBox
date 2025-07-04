from fastapi import APIRouter, Depends, HTTPException, status
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
        return await service.get_cart(current_user.id)
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
