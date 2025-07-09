from typing import List

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Allergy, UserForm, user_allergies
from app.repositories.base import BaseRepository


class AllergyRepository(BaseRepository[Allergy]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Allergy)

    async def update_form_allergies(
            self, user_id: int, allergy_ids: List[int]
    ) -> None:

        try:

            await self.db.execute(
                delete(user_allergies).where(user_allergies.c.user_id == user_id))

            if allergy_ids:
                if not all(isinstance(aid, int) for aid in allergy_ids):
                    raise ValueError("Все allergy_ids должны быть целыми числами")

                existing = await self.db.execute(
                    select(Allergy.id).where(Allergy.id.in_(allergy_ids)))
                existing_ids = {r[0] for r in existing}
                if len(existing_ids) != len(set(allergy_ids)):
                    raise ValueError("Некоторые аллергии не существуют")

                await self.db.execute(
                    insert(user_allergies),
                    [{"user_id": user_id, "allergy_id": aid} for aid in allergy_ids]
                )

            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError(f"Ошибка обновления аллергий: {e}") from e

    async def get_by_ids(self, ids: List[int]) -> List[Allergy]:
        if not ids:
            return []

        result = await self.db.execute(
            select(Allergy).where(Allergy.id.in_(ids))
        )
        return list(result.scalars().all())
