from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel, BaseModel
from datetime import date

db_schema = 'ckl'

class Countries(BaseModel):
    __tablename__ = 'countries'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код страны', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
