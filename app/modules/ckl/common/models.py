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

class Currencies(BaseModel):
    __tablename__ = 'currencies'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код марки ТС', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)

class Kato(BaseModel):
    __tablename__ = 'kato'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код КАТО', nullable=False)
    level: Mapped[int] = mapped_column(name='level', comment='Уровень', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    parent_code: Mapped[str] = mapped_column(name='parent_code', comment='Код КАТО родительского объекта', nullable=True)

class TnVed(BaseModel):
    __tablename__ = 'tn_ved'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код ТН ВЭД', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey('ckl.tn_ved.id'), comment='Родитель', nullable=True)
    level: Mapped[int] = mapped_column(name='level', comment='Уровень вложенности', nullable=False)

class UnitsOfMeasure(BaseModel):
    __tablename__ = 'units_of_measure'
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)