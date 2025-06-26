from typing import List

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    users: Mapped[List["UserForm"]] = relationship(
        secondary="user_goals", back_populates="goals"
    )


class Allergy(Base):
    __tablename__ = "allergies"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    users: Mapped[List["UserForm"]] = relationship(
        secondary="user_allergies", back_populates="allergies"
    )
