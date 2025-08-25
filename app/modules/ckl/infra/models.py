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
