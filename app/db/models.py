from __future__ import annotations

from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Brew(Base):
    __tablename__ = "brews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    coffee: Mapped[str] = mapped_column(String(200), nullable=False)
    dose: Mapped[float] = mapped_column(Float, nullable=False)
    ratio: Mapped[float] = mapped_column(Float, nullable=False, default=16.0)
    water: Mapped[float] = mapped_column(Float, nullable=False)

    temperature: Mapped[int] = mapped_column(Integer, nullable=False, default=94)
    grind: Mapped[str] = mapped_column(String(30), nullable=False, default="medium")

    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
