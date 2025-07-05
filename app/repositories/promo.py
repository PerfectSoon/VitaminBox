from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Promo
from app.repositories.base import BaseRepository


class PromoRepository(BaseRepository[Promo]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Promo)

    async def get_by_code(self, code: str) -> Promo | None:
        query = select(Promo).where(Promo.code == code)
        result = await self.db.execute(query)
        return result.scalars().first()
