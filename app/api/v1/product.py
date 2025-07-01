from typing import List

from fastapi import APIRouter, HTTPException, Depends, status

from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    ServiceError,
    UserNotFoundError,
    EntityNotFound,
)
from app.schemas import (
    ProductOut,
    ProductCreate,
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
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductOut]:
    try:
        return await product_service.get_all_product()
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
