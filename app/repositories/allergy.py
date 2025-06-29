from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Allergy
from app.repositories.base import BaseRepository


class AllergyRepository(BaseRepository[Allergy]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Allergy)
