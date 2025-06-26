from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        try:
            res = await self.db.execute(select(User).where(User.email == email))
            return res.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Ошибка при получении пользователя: {e}")
