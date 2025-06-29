from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.service_errors import ServiceError
from app.models import Goal
from app.repositories.base import BaseRepository, T


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Goal)
