from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models import Goal, UserForm
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Goal)

    async def update_form_goals(
        self, user_id: int, goal_ids: List[int]
    ) -> None:

        user_form_goals = UserForm.__table__.c.goals.association_table

        try:

            await self.db.execute(
                delete(user_form_goals).where(
                    user_form_goals.c.user_id == user_id
                )
            )

            if goal_ids:
                if not all(isinstance(gid, int) for gid in goal_ids):
                    raise ValueError("Все goal_ids должны быть целыми числами")

                await self.db.execute(
                    insert(user_form_goals),
                    [{"user_id": user_id, "goal_id": gid} for gid in goal_ids],
                )

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise e
