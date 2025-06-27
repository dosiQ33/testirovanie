from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BasestModel


class KazgeodesyRkOblasti(BasestModel):
    __tablename__ = "KAZGEODESY_RK_OBLASTI"
    __table_args__ = dict(schema="ext", comment="Области РК")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, comment="ID родителя", nullable=True)

    type: Mapped[str] = mapped_column(Integer, comment="Тип", nullable=True)

    name_ru: Mapped[str] = mapped_column(Integer, comment="Наименование РУС", nullable=True)

    kato: Mapped[str] = mapped_column(Integer, comment="КАТО", nullable=True)
    parentkato: Mapped[str] = mapped_column(Integer, comment="Родительский КАТО", nullable=True)

    geom: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class KazgeodesyRkRaiony(BasestModel):
    __tablename__ = "KAZGEODESY_RK_RAIONY"
    __table_args__ = dict(schema="ext", comment="Районы РК")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, comment="ID родителя", nullable=True)

    type: Mapped[str] = mapped_column(Integer, comment="Тип", nullable=True)

    name_ru: Mapped[str] = mapped_column(Integer, comment="Наименование РУС", nullable=True)

    kato: Mapped[str] = mapped_column(Integer, comment="КАТО", nullable=True)
    parentkato: Mapped[str] = mapped_column(Integer, comment="Родительский КАТО", nullable=True)

    geom: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )
