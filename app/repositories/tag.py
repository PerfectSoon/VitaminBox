from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tag, Product
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Tag)

    async def update_product_tags(
        self, product_id: int, tag_ids: List[int]
    ) -> None:

        product_tags = Product.__table__.c.tags.association_table

        try:

            await self.db.execute(
                delete(product_tags).where(
                    product_tags.c.product_id == product_id
                )
            )

            if tag_ids:
                if not all(isinstance(tid, int) for tid in tag_ids):
                    raise ValueError("Все tag_ids должны быть целыми числами")

                existing_tags = await self.get_by_ids(tag_ids)
                if len(existing_tags) != len(tag_ids):
                    raise ValueError("Некоторые теги не существуют")

                await self.db.execute(
                    insert(product_tags),
                    [
                        {"product_id": product_id, "tag_id": tid}
                        for tid in tag_ids
                    ],
                )

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_ids(self, tag_ids: List[int]) -> List[Tag]:

        if not tag_ids:
            return []

        result = await self.db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        return list(result.scalars().all())
