from typing import List

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Allergy, UserForm
from app.repositories.base import BaseRepository


class AllergyRepository(BaseRepository[Allergy]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Allergy)

    async def update_form_allergies(
        self, user_id: int, allergy_ids: List[int]
    ) -> None:
        user_form_allergies = UserForm.__table__.c.allergies.association_table

        try:
            await self.db.execute(
                delete(user_form_allergies).where(
                    user_form_allergies.c.user_id == user_id
                )
            )

            if allergy_ids:
                if not all(isinstance(aid, int) for aid in allergy_ids):
                    raise ValueError(
                        "Все allergy_ids должны быть целыми числами"
                    )

                existing_allergies = await self.get_by_ids(allergy_ids)
                if len(existing_allergies) != len(allergy_ids):
                    raise ValueError("Некоторые аллергии не существуют")

                await self.db.execute(
                    insert(user_form_allergies),
                    [
                        {"user_id": user_id, "allergy_id": aid}
                        for aid in allergy_ids
                    ],
                )

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_ids(self, ids: List[int]) -> List[Allergy]:
        if not ids:
            return []

        result = await self.db.execute(
            select(Allergy).where(Allergy.id.in_(ids))
        )
        return list(result.scalars().all())
