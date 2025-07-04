from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.core.types import Gender
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
    name: Optional[str] = Query(
        None, description="Фильтр по названию товара (частичное совпадение)"
    ),
    min_price: Optional[float] = Query(
        None, gt=0, description="Минимальная цена"
    ),
    max_price: Optional[float] = Query(
        None, gt=0, description="Максимальная цена"
    ),
    min_age: Optional[int] = Query(
        None, ge=0, description="Минимальный возраст"
    ),
    gender: Optional[Gender] = Query(None, description="Фильтр по полу"),
    is_active: Optional[bool] = Query(
        True, description="Фильтр по активности товара"
    ),
    skip: int = 0,
    limit: int = 100,
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductOut]:
    try:
        filters = {
            "name": name,
            "min_price": min_price,
            "max_price": max_price,
            "min_age": min_age,
            "gender": gender,
            "is_active": is_active,
        }
        return await product_service.get_all_product(
            skip=skip, limit=limit, filters=filters
        )
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
