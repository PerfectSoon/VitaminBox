from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models import Goal, user_goals
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Goal)

    async def update_form_goals(
        self, user_id: int, goal_ids: List[int]
    ) -> None:

        try:

            await self.db.execute(
                delete(user_goals).where(user_goals.c.user_id == user_id)
            )
            if goal_ids:
                if not all(isinstance(gid, int) for gid in goal_ids):
                    raise ValueError("Все goal_ids должны быть целыми числами")

                existing = await self.db.execute(
                    select(Goal.id).where(Goal.id.in_(goal_ids))
                )
                existing_ids = {r[0] for r in existing}
                if len(existing_ids) != len(set(goal_ids)):
                    raise ValueError("Некоторые цели не существуют")

                await self.db.execute(
                    insert(user_goals),
                    [{"user_id": user_id, "goal_id": gid} for gid in goal_ids],
                )

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise RuntimeError(f"Ошибка обновления целей: {e}") from e
