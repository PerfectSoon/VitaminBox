from datetime import date

from sqlalchemy import ForeignKey, Date, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VitaminIntake(Base):
    __tablename__ = "vitamin_intakes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    intake_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    is_taken: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    dose: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship(back_populates="vitamin_intakes")
    product: Mapped["Product"] = relationship()
