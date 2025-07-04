from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.types import OrderStatus
from app.exceptions.service_errors import EntityNotFound
from app.models import Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Order)

    async def get_pending_order(self, user_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .where(
                Order.user_id == user_id, Order.status == OrderStatus.PENDING
            )
            .options(selectinload(Order.items))
        )
        return result.scalars().first()

    async def update_cart(
        self, order_id: int, items: list[dict], total_amount: float
    ) -> Order:
        order = await self.get_by_id(order_id)
        if not order:
            raise EntityNotFound("Заказ не найден")

        order.total_amount = total_amount

        await self.db.execute(
            delete(OrderItem).where(OrderItem.order_id == order_id)
        )
        await self.db.flush()

        for item_data in items:
            item = OrderItem(order_id=order_id, **item_data)
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(order)
        return order
