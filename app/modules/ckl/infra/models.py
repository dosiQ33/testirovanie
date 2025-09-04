from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel, BaseModel
from datetime import date

db_schema = "ckl"


def mapped_multilinestring_column() -> Mapped[WKBElement]:
    return mapped_column(
        Geometry(geometry_type="MULTILINESTRING", srid=4326, spatial_index=True),
        comment="Координаты",
        nullable=True,
    )


class RoadTypes(BaseModel):
    __tablename__ = "road_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str] = mapped_column(
        name="name_kk", comment="Наименование на казахском языке", nullable=False
    )
    name_ru: Mapped[str] = mapped_column(
        name="name_ru", comment="Наименование на русском языке", nullable=False
    )


class Roads(BaseModel):
    __tablename__ = "roads"
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name="code", comment="Код дороги", nullable=False)
    name: Mapped[str] = mapped_column(
        name="name", comment="Название дороги", nullable=False
    )
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.roads.id"), comment="Родительская дорога", nullable=True
    )
    kato_code: Mapped[str] = mapped_column(
        name="kato_code",
        comment="Область или регион прохождения участка",
        nullable=True,
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.road_types.id"), comment="Тип дороги", nullable=True
    )
    shape: Mapped[int] = mapped_multilinestring_column()

class Cameras(BaseModel):
    __tablename__ = 'cameras'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код камеры', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    shape: Mapped[int] = mapped_column(name='shape', comment='Координаты GPS', nullable=False)
    address: Mapped[str] = mapped_column(name='address', comment='Адрес или описание расположения', nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('ckl.camera_types.id'), comment='Тип камеры', nullable=True)
    is_active: Mapped[bool] = mapped_column(name='is_active', comment='Активна ли камера в системе', nullable=False)
    installation_date: Mapped[date] = mapped_column(name='installation_date', comment='Дата установки камеры', nullable=False)
    camera_operator_id: Mapped[int] = mapped_column(ForeignKey('ckl.camera_operators.id'), comment='Ссылка на оператора камер', nullable=True)
    roads_id: Mapped[int] = mapped_column(ForeignKey('ckl.roads.id'), comment='Ссылка на дорогу', nullable=True)
