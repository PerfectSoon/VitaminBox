from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    EntityNotFound,
)
from app.schemas import (
    ProductOut,
    ProductCreate,
    TagCreate,
    TagOut,
    CategoryOut,
    CategoryCreate,
)

from app.api.dependencies import get_product_service
from app.services.product import ProductService

router = APIRouter()


@router.get(
    "/",
    response_model=List[ProductOut],
    summary="Получить все товары",
    responses={
        404: {"description": "Список товаров пуст"},
        200: {"description": "Успешное получение списка товаров"},
    },
)
async def get_all_products(
    is_active: Optional[bool] = Query(
        True,
        description="Фильтр по не деактивированым товарам (по умолчанию True)",
    ),
    skip: int = 0,
    limit: int = 100,
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductOut]:
    try:
        filters = {"is_active": is_active}
        return await product_service.get_all_product(
            skip=skip, limit=limit, filters=filters
        )
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
