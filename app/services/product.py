import asyncio
from dataclasses import dataclass
from typing import List, Optional
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

from app.schemas import (
    ProductOut,
    ProductCreate,
    CategoryOut,
    CategoryCreate,
    TagCreate,
    TagOut,
    ProductUpdate,
    ProductListResponse,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class ProductService:
    product_repository: ProductRepository
    category_repository: CategoryRepository
    tag_repository: TagRepository

    async def create_category(
        self, category_data: CategoryCreate
    ) -> CategoryOut:
        if await self.category_repository.get_by_name(category_data.name):
            raise EntityAlreadyExistsError(
                "Категория с таким названием уже существует"
            )
        res = await self.category_repository.create(category_data.model_dump())
        return CategoryOut.model_validate(res)

    async def create_tag(self, tag_data: TagCreate) -> TagOut:
        if await self.tag_repository.get_by_name(tag_data.name):
            raise EntityAlreadyExistsError(
                "Тэг с таким названием уже существует"
            )
        res = await self.tag_repository.create(tag_data.model_dump())
        return TagOut.model_validate(res)

    async def get_categories(self) -> List[CategoryOut]:
        list_cats = await self.category_repository.get_all()
        if not list_cats:
            raise EntityNotFound(f"Список категорий пуст")
        return [CategoryOut.model_validate(cat) for cat in list_cats]

    async def get_tags(self) -> List[TagOut]:
        list_tags = await self.tag_repository.get_all()
        if not list_tags:
            raise EntityNotFound(f"Список тэгов пуст")
        return [TagOut.model_validate(tag) for tag in list_tags]

    async def get_product_by_id(self, product_id: int) -> ProductOut:
        product = await self.product_repository.get_by_id(product_id)

        if not product:
            raise EntityNotFound(f"Продукта с ID={product_id} не существует")

        return ProductOut.model_validate(product)

    async def update_product_by_id(
        self, product_id: int, product_data: ProductUpdate
    ) -> ProductOut:
        product = await self.product_repository.get_by_id(product_id)

        if not product:
            raise EntityNotFound(f"Продукта с ID={product_id} не существует")

        updated_data = product_data.model_dump(
            exclude_unset=True, exclude={"tag_ids"}
        )

        updated_product = await self.product_repository.update(
            product, updated_data
        )
        print(updated_product)

        if product_data.tag_ids is not None:
            tags = await self.tag_repository.get_by_ids(product_data.tag_ids)
            product.tags = tags
            await self.tag_repository.db.commit()

        await self.product_repository.db.refresh(product)
        if not updated_product:
            raise EntityNotFound("Не удалось обновить продукт")

        return ProductOut.model_validate(updated_product)

    async def get_all_product(
        self, skip: int, limit: int, filters: Optional[dict] = None
    ) -> ProductListResponse:
        list_products = await self.product_repository.get_all_products(
            skip=skip, limit=limit, **(filters if filters else {})
        )

        if not list_products:
            raise EntityNotFound(f"Список продуктов пуст")

        total = await self.product_repository.count()

        return ProductListResponse(
            total=total,
            products=[ProductOut.model_validate(prod) for prod in list_products]
        )

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
                f"Категории с ID={product_data.category_id} не существует"
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

    async def delete_product(self, product_id: int) -> None:
        product = await self.product_repository.get_by_id(product_id)

        if not product:
            raise EntityNotFound(f"Продукт с id {product_id} не найден")

        await self.product_repository.delete(product_id)

    async def deactivate_product(self, product_id: int) -> None:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFound("Товар не найден")

        await self.product_repository.deactivate_product(product)

    async def activate_product(self, product_id: int) -> None:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFound("Товар не найден")

        await self.product_repository.activate_product(product)

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repository.get_by_id(category_id)

        if not category:
            raise EntityNotFound(f"Категория с id {category_id} не найден")

        await self.category_repository.delete(category_id)

    async def delete_tag(self, tag_id: int) -> None:
        tag = await self.tag_repository.get_by_id(tag_id)

        if not tag:
            raise EntityNotFound(f"Тэг с id {tag_id} не найден")

        await self.tag_repository.delete(tag_id)
