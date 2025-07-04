from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Promo
from app.repositories.base import BaseRepository


class PromoRepository(BaseRepository[Promo]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Promo)
