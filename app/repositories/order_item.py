from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderItem
from app.repositories.base import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, OrderItem)

    async def add_order_item(self, order_id: int, item_data: dict) -> OrderItem:
        item = OrderItem(order_id=order_id, **item_data)
        self.db.add(item)
        await self.db.commit()
        return item

    async def delete_by_order_id(self, order_id: int):
        await self.db.execute(
            delete(OrderItem).where(OrderItem.order_id == order_id)
        )
        await self.db.commit()
