from typing import Optional, List

from pydantic import BaseModel, Field

from app.core.types import OrderStatus


class PromoBase(BaseModel):
    code: str = Field(max_length=20)
    discount_percent: int = Field(gt=0, le=100)


class PromoCreate(PromoBase):
    pass


class PromoUpdate(BaseModel):
    is_available: Optional[bool] = None


class PromoOut(PromoBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)
    price: int = Field(default=1, gt=0)


class OrderItemOut(OrderItemBase):
    id: int

    class Config:
        from_attributes = True


class OrderItemCreate(OrderItemBase):
    pass


class OrderCreate(BaseModel):
    user_id: Optional[int] = None
    promo_code: Optional[str] = None
    items: List[OrderItemOut]


class OrderOut(BaseModel):
    id: int
    user_id: Optional[int]
    status: OrderStatus
    total_amount: float
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
