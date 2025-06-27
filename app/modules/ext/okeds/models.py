from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel


class Okeds(BasestModel):
    __tablename__ = "okeds"
    __table_args__ = dict(schema="ext", comment="ОКЭДы")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(comment="Код ОКЕД")
    name_ru: Mapped[str] = mapped_column(comment="Наименование РУС")
    name_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
