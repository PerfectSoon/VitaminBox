import asyncio
from dataclasses import dataclass
from itertools import product
from typing import List
from sqlalchemy.exc import IntegrityError

from app.exceptions.service_errors import (
    UserNotFoundError,
    EntityAlreadyExistsError,
    ServiceError,
    EntityNotFound,
)


from app.repositories import (
    ProductRepository,
    CategoryRepository,
    TagRepository,
)

from app.schemas import ProductOut, ProductCreate


@dataclass(kw_only=True, frozen=True, slots=True)
class ProductService:
    product_repository: ProductRepository
    category_repository: CategoryRepository
    tag_repository: TagRepository

    async def get_all_product(self) -> List[ProductOut]:
        list_products = await self.product_repository.get_all()
        print(
            "ГДЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕ МОИ ПРОДУКТЫ",
            list_products,
        )
        if not list_products:
            raise EntityNotFound(f"Список продуктов пуст")
        return [ProductOut.model_validate(prod) for prod in list_products]

    async def create_product(self, product_data: ProductCreate) -> ProductOut:
        existing = await self.product_repository.get_by_name(product_data.name)
        if existing:
            raise EntityAlreadyExistsError(
                f"Товар с именем - {product_data.name} уже существует"
            )

        existed_category = await self.category_repository.get_by_id(
            product_data.category_id
        )
        if not existed_category:
            raise EntityNotFound(
                f"Категории с ID={product_data.name} не существует"
            )
        if product_data.tag_ids:
            existed_tags = await asyncio.gather(
                *[
                    self.tag_repository.get_by_id(tag_id)
                    for tag_id in product_data.tag_ids
                ]
            )
            if None in existed_tags:
                invalid_tags = [
                    tag_id
                    for tag_id, tag in zip(product_data.tag_ids, existed_tags)
                    if tag is None
                ]
                raise EntityNotFound(f"Теги с ID={invalid_tags} не существуют")

        base_data = product_data.model_dump(exclude={"tag_ids"})

        try:
            product_orm = await self.product_repository.create_product(
                prod_data=base_data,
                tag_ids=product_data.tag_ids,
            )

            return ProductOut.model_validate(product_orm)

        except IntegrityError as e:
            if "foreign_key" in str(e.orig).lower():
                raise ServiceError("Нарушение ссылочной целостности данных")
            raise ServiceError("Ошибка сохранения товара в базу данных")
