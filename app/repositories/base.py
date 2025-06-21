from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, true, false

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        return await self.db.get(self.model, id)

    async def get_all(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> List[T]:
        query = select(self.model).offset(skip).limit(limit)
        for field, value in filters.items():
            col = getattr(self.model, field)
            if isinstance(value, bool):
                query = query.where(col == (true() if value else false()))
            else:
                query = query.where(col == value)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_data: dict) -> T:
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except:
            await self.db.rollback()
            raise

    async def update(self, db_obj: T, obj_data: dict) -> T:
        if not db_obj:
            raise ValueError("Объект для обновления не найден")
        for field, value in obj_data.items():
            if not hasattr(db_obj, field):
                raise ValueError(f"Поле {field} не существует")
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id_el: int) -> None:
        res = await self.db.execute(
            delete(self.model).where(self.model.id == id_el)
        )
        if res.rowcount == 0:
            raise ValueError(f"ID={id_el} не найден")
        await self.db.commit()
