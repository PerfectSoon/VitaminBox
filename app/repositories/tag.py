from typing import List

from select import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Tag)

    async def get_by_ids(self, ids: List[int]) -> List[Tag]:
        if not ids:
            return []

        result = await self.db.execute(select(Tag).where(Tag.id.in_(ids)))
        return list(result.scalars().all())
