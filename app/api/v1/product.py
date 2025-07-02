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


# --- Категории ---
@router.post(
    "/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую категорию",
    responses={
        409: {"description": "Категория с таким названием уже существует"},
        201: {"description": "Категория успешно создана"},
    },
)
async def create_category(
    category_data: CategoryCreate,
    product_service: ProductService = Depends(get_product_service),
) -> CategoryOut:
    try:
        return await product_service.create_category(category_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# --- Теги ---
@router.post(
    "/tags",
    response_model=TagOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый тег",
    responses={
        409: {"description": "Тег с таким названием уже существует"},
        201: {"description": "Тег успешно создан"},
    },
)
async def create_tag(
    tag_data: TagCreate,
    product_service: ProductService = Depends(get_product_service),
) -> TagOut:
    try:
        return await product_service.create_tag(tag_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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


@router.post(
    "/",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый товар",
    responses={
        400: {"description": "Некорректные данные"},
        404: {"description": "Категория или тег не найдены"},
        409: {"description": "Товар с таким именем уже существует"},
        500: {"description": "Ошибка сервера при создании товара"},
    },
)
async def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
) -> ProductOut:
    try:
        return await product_service.create_product(product_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "Произошла ошибка при создании товара",
                "err": str(e),
            },
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
    responses={
        404: {"description": "Товар не найден"},
        204: {"description": "Товар успешно удален"},
    },
)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> None:
    try:
        await product_service.delete_product(product_id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.patch(
    "/{product_id}/deactivate",
    status_code=status.HTTP_200_OK,
    summary="Деактивировать товар",
    responses={
        404: {"description": "Товар не найден"},
        200: {"description": "Товар успешно деактивирован"},
    },
)
async def deactivate_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    try:
        await product_service.deactivate_product(product_id)
        return {"message": "Товар успешно деактивирован"}
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.patch(
    "/{product_id}/activate",
    status_code=status.HTTP_200_OK,
    summary="Активировать деактивированный товар",
    responses={
        404: {"description": "Товар не найден"},
        200: {"description": "Деактивированный товар успешно активирован"},
    },
)
async def activate_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    try:
        await product_service.activate_product(product_id)
        return {"message": "Товар успешно активирован"}
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
