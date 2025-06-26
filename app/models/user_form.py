from typing import List

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Enum as SAEnum,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import Gender

from app.models.base import Base


user_goals = Table(
    "user_goals",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user_forms.user_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "goal_id", ForeignKey("goals.id", ondelete="CASCADE"), primary_key=True
    ),
)
user_allergies = Table(
    "user_allergies",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user_forms.user_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "allergy_id",
        ForeignKey("allergies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class UserForm(Base):
    __tablename__ = "user_forms"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Gender] = mapped_column(SAEnum(Gender), nullable=False)

    user: Mapped["User"] = relationship(back_populates="user_form")

    goals: Mapped[List["Goal"]] = relationship(
        secondary=user_goals, back_populates="users"
    )
    allergies: Mapped[List["Allergy"]] = relationship(
        secondary=user_allergies, back_populates="users"
    )
