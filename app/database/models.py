from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    Enum as SAEnum,
    DateTime,
    func,
    ForeignKey,
    Float,
    Boolean,
    Date,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
    declared_attr,
)
from app.core.types import UserType, OrderStatus


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__.lower()
        return name + "s" if not name.endswith("s") else name


class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserType] = mapped_column(
        SAEnum(UserType), default=UserType.USER, nullable=False
    )
    user_form = relationship(
        "UserForm", back_populates="user", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="user")
    vitamin_intakes = relationship("VitaminIntake", back_populates="user")


class UserForm(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    user = relationship("User", back_populates="user_form")


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )


class Product(Base):
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    promo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("promos.id"))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")


class OrderItem(Base):
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE")
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Promo(Base):
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


class VitaminIntake(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    intake_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    is_taken: Mapped[bool] = mapped_column(Boolean, default=False)
    dose: Mapped[float] = mapped_column(Float)

    user = relationship("User", back_populates="vitamin_intakes")
    product = relationship("Product")
