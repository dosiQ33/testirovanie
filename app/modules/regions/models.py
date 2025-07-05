from __future__ import annotations
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from app.modules.common.models import BasestModel


class Populations(BasestModel):
    __tablename__ = "populations"
    __table_args__ = dict(comment="население")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    oblast_id: Mapped[int] = mapped_column(ForeignKey("ext.KAZGEODESY_RK_OBLASTI.id"), comment="области", nullable=True)
    raion_id: Mapped[int] = mapped_column(ForeignKey("ext.KAZGEODESY_RK_RAIONY.id"), comment="районы", nullable=True)

    date_: Mapped[date] = mapped_column(name="date", comment="дата", nullable=True)

    people_num: Mapped[int] = mapped_column(Integer, comment="число людей", nullable=True)
    male_num: Mapped[int] = mapped_column(Integer, comment="число мужчин", nullable=True)
    female_num: Mapped[int] = mapped_column(Integer, comment="число женщин", nullable=True)