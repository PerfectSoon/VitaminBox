from dataclasses import dataclass

from app.exceptions.service_errors import EntityNotFound

from app.repositories import OrderRepository, ProductRepository
from app.schemas import OrderOut, OrderStatus, OrderItemCreate


@dataclass(kw_only=True, frozen=True, slots=True)
class OrderService:
    order_repository: OrderRepository
    product_repository: ProductRepository

    async def get_active_cart(self, user_id: int) -> OrderOut:
        order = await self.order_repository.get_pending_order(user_id)
        if not order:
            order_data = {
                "user_id": user_id,
                "status": OrderStatus.PENDING,
                "total_amount": 0,
            }
            order = await self.order_repository.create(order_data)
        return OrderOut.model_validate(order)

    async def add_item_to_cart(
        self, user_id: int, item_data: OrderItemCreate
    ) -> OrderOut:
        order = await self.get_active_cart(user_id)

        product = await self.product_repository.get_by_id(item_data.product_id)
        if not product:
            raise EntityNotFound("Продукт не найден")

        updated_items = []
        item_found = False

        for item in order.items:
            if item.product_id == item_data.product_id:
                updated_items.append(
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity + item_data.quantity,
                        "price": item_data.price,
                    }
                )
                item_found = True
            else:
                updated_items.append(
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item_data.price,
                    }
                )

        if not item_found:
            updated_items.append(
                {
                    "product_id": item_data.product_id,
                    "quantity": item_data.quantity,
                    "price": item_data.price,
                }
            )

        total_amount = 0
        for item in updated_items:
            prod = await self.product_repository.get_by_id(item["product_id"])
            if not prod:
                raise EntityNotFound(
                    f"Продукт с id {item['product_id']} не найден"
                )
            total_amount += item["quantity"] * prod.price

        updated_order = await self.order_repository.update_cart(
            order_id=order.id, items=updated_items, total_amount=total_amount
        )

        return OrderOut.model_validate(updated_order)

    async def get_cart(self, user_id: int) -> OrderOut:
        order = await self.get_active_cart(user_id)
        return OrderOut.model_validate(order)

    async def remove_item_from_cart(
        self, user_id: int, product_id: int
    ) -> OrderOut:
        order = await self.get_active_cart(user_id)

        updated_items = []
        for item in order.items:
            if item.product_id == product_id:
                if item.quantity > 1:
                    updated_items.append(
                        {
                            "id": item.id,
                            "product_id": item.product_id,
                            "quantity": item.quantity - 1,
                            "price": item.price,
                        }
                    )

            else:
                updated_items.append(
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price,
                    }
                )

        total_amount = 0
        for item in updated_items:
            prod = await self.product_repository.get_by_id(item["product_id"])
            if not prod:
                raise EntityNotFound(
                    f"Продукт с id {item['product_id']} не найден"
                )
            total_amount += item["quantity"] * prod.price

        updated_order = await self.order_repository.update_cart(
            order_id=order.id, items=updated_items, total_amount=total_amount
        )

        return OrderOut.model_validate(updated_order)

    async def confirm_order(self, user_id: int) -> OrderOut:
        order = await self.order_repository.get_pending_order(user_id)
        if not order or not order.items:
            raise EntityNotFound("Корзина пуста или не найдена")

        updated_order = await self.order_repository.update(
            order, {"status": OrderStatus.CONFIRMED}
        )
        return OrderOut.model_validate(updated_order)
