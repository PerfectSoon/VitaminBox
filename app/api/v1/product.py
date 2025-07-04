from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.core.types import Gender
from app.exceptions.service_errors import (
    EntityNotFound,
)
from app.schemas import (
    ProductOut,
    CategoryOut,
    TagOut,
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


@router.get(
    "/categories",
    response_model=List[CategoryOut],
    summary="Получить все категории",
    responses={
        404: {"description": "Список категорий пуст"},
        200: {"description": "Успешное получение списка категорий"},
    },
)
async def get_all_categories(
    service: ProductService = Depends(get_product_service),
) -> List[CategoryOut]:
    try:
        return await service.get_categories()
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/tags",
    response_model=List[TagOut],
    summary="Получить все тэги",
    responses={
        404: {"description": "Список тэгов пуст"},
        200: {"description": "Успешное получение списка тэгов"},
    },
)
async def get_all_tags(
    service: ProductService = Depends(get_product_service),
) -> List[TagOut]:
    try:
        return await service.get_tags()
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Получить продукт по id",
    responses={
        404: {"description": "Продукта с таким ID не существует"},
        200: {"description": "Продукт получен успешно"},
    },
)
async def get_product_by_id(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> ProductOut:
    try:
        return await service.get_product_by_id(product_id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
