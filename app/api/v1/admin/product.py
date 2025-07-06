from fastapi import Depends, HTTPException, status, APIRouter

from app.api.dependencies import get_product_service, get_current_admin
from app.exceptions.service_errors import (
    EntityAlreadyExistsError,
    EntityNotFound,
    ServiceError,
)
from app.schemas import (
    ProductOut,
    ProductCreate,
    TagOut,
    TagCreate,
    CategoryOut,
    CategoryCreate,
    ProductUpdate,
    UserOut,
)
from app.services import ProductService

router = APIRouter()


@router.post(
    "/products",
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
    admin: UserOut = Depends(get_current_admin),
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
    admin: UserOut = Depends(get_current_admin),
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
    admin: UserOut = Depends(get_current_admin),
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
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    try:
        await product_service.activate_product(product_id)
        return {"message": "Товар успешно активирован"}
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


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
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> TagOut:
    try:
        return await product_service.create_tag(tag_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> CategoryOut:
    try:
        return await product_service.create_category(category_data)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить категорию",
    responses={
        404: {"description": "Категория не найден"},
        204: {"description": "Категория успешно удалена"},
    },
)
async def delete_category(
    category_id: int,
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> None:
    try:
        await product_service.delete_category(category_id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тэг",
    responses={
        404: {"description": "тэг не найден"},
        204: {"description": "тэг успешно удален"},
    },
)
async def delete_tag(
    tag_id: int,
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> None:
    try:
        await product_service.delete_tag(tag_id)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Обновить товар",
    responses={
        200: {"description": "Товар успешно обновлен"},
        404: {"description": "Товар не найден"},
        400: {"description": "Некорректные данные"},
        422: {"description": "Ошибка валидации данных"},
    },
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    admin: UserOut = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
) -> ProductOut:
    try:
        await product_service.update_product_by_id(product_id, product_data)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
