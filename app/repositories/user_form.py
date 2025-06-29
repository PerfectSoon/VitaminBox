from typing import List, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models import UserForm, Goal, Allergy
from app.repositories.base import BaseRepository, T


class UserFormRepository(BaseRepository[UserForm]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserForm)

    async def get_user_form(self, user_id: int) -> UserForm:
        try:
            res = await self.db.execute(
                select(UserForm).where(UserForm.user_id == user_id)
            )
            return res.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Ошибка при получении анкеты пользователя: {e}")

    async def create_user_form(
        self,
        user_id: int,
        form_data: dict,
        goal_ids: List[int] | None = None,
        allergy_ids: List[int] | None = None,
    ) -> UserForm:
        user_form = UserForm(user_id=user_id, **form_data)
        self.db.add(user_form)

        if goal_ids:
            goals = await self._get_related_objects(Goal, goal_ids)
            user_form.goals.extend(goals)

        if allergy_ids:
            allergies = await self._get_related_objects(Allergy, allergy_ids)
            user_form.allergies.extend(allergies)

        try:
            await self.db.commit()
            await self.db.refresh(user_form, ["goals", "allergies"])
            return user_form
        except Exception as e:
            await self.db.rollback()
            raise e

    async def _get_related_objects(
        self, model: Type[T], ids: List[int]
    ) -> List[T]:
        if not ids:
            return []

        result = await self.db.execute(select(model).where(model.id.in_(ids)))
        objects = result.scalars().all()

        if len(objects) != len(ids):
            found_ids = {obj.id for obj in objects}
            not_found = set(ids) - found_ids
            raise ValueError(
                f"Объекты {model.__name__} с ID={not_found} не найдены"
            )
        return list(objects)
