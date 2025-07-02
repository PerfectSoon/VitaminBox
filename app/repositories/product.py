from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Tag
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)

    async def create_product(
        self,
        prod_data: dict,
        tag_ids: List[int] | None = None,
    ) -> Product:

        product = Product(**prod_data)
        self.db.add(product)

        if tag_ids:
            tags = await self._get_related_objects(Tag, tag_ids)
            product.tags.extend(tags)

        try:
            await self.db.commit()
            await self.db.refresh(product, ["tags"])
            return product
        except Exception as e:
            await self.db.rollback()
            raise e

    async def deactivate_product(self, product: Product) -> None:
        try:
            product.is_active = False
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
