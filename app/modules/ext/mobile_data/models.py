from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from decimal import Decimal
from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BasestModel

if TYPE_CHECKING:
    from app.modules.ext.kazgeodesy.models import (
        KazgeodesyRkOblasti,
        KazgeodesyRkRaiony,
    )


class KaztelecomHour(BasestModel):
    __tablename__ = "kaztelecom_hour"
    __table_args__ = dict(schema="ext", comment="Справочник часов Казтелеком")

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hourly_cut: Mapped[Optional[str]] = mapped_column(comment="Часовой интервал")

    # # Relationships
    # mobile_data: Mapped[List["KaztelecomMobileData"]] = relationship(
    #     "KaztelecomMobileData", back_populates="hour", lazy="selectin"
    # )


class KaztelecomStationsGeo(BasestModel):
    __tablename__ = "kaztelecom_stations_geo"
    __table_args__ = dict(
        schema="ext", comment="Геопространственные данные станций Казтелеком"
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    diag_size: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Размер диагонали"
    )

    # Coordinates
    lat_bot_left: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Широта нижний левый"
    )
    long_bot_left: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Долгота нижний левый"
    )
    lat_bot_right: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Широта нижний правый"
    )
    long_bot_right: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Долгота нижний правый"
    )
    lat_top_right: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Широта верхний правый"
    )
    long_top_right: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Долгота верхний правый"
    )
    lat_top_left: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Широта верхний левый"
    )
    long_top_left: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Долгота верхний левый"
    )
    lat_center: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Широта центра"
    )
    long_center: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 3), comment="Долгота центра"
    )

    # Geometry
    polygon_wkt: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True),
        comment="Геометрия полигона",
        nullable=True,
    )

    # Location info
    region: Mapped[Optional[str]] = mapped_column(comment="Регион")
    city: Mapped[Optional[str]] = mapped_column(comment="Город")
    district: Mapped[Optional[str]] = mapped_column(comment="Район")

    # Foreign keys
    oblast_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ext.KAZGEODESY_RK_OBLASTI.id"), comment="ID области"
    )
    raion_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ext.KAZGEODESY_RK_RAIONY.id"), comment="ID района"
    )

    # Zone info
    in_special_zone: Mapped[Optional[int]] = mapped_column(
        Integer, comment="В специальной зоне"
    )
    zone_id: Mapped[Optional[int]] = mapped_column(Integer, comment="ID зоны")
    zone_type: Mapped[Optional[int]] = mapped_column(Integer, comment="Тип зоны")

    # Relationships (опционально, если нужны связи с казгеодезией)
    # oblast: Mapped[Optional["KazgeodesyRkOblasti"]] = relationship("KazgeodesyRkOblasti", lazy="selectin")
    # raion: Mapped[Optional["KazgeodesyRkRaiony"]] = relationship("KazgeodesyRkRaiony", lazy="selectin")


class KaztelecomMobileData(BasestModel):
    __tablename__ = "kaztelecom_mobile_data"
    __table_args__ = dict(schema="ext", comment="Мобильные данные Казтелеком")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Optional[date]] = mapped_column(Date, comment="Дата")

    # Foreign keys
    hour_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ext.kaztelecom_hour.id"), comment="ID часа"
    )

    # Zone and demographic data
    zid_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="ZID ID")
    age_id: Mapped[Optional[int]] = mapped_column(Integer, comment="ID возраста")
    income_id: Mapped[Optional[int]] = mapped_column(Integer, comment="ID дохода")
    gender_id: Mapped[Optional[int]] = mapped_column(Integer, comment="ID пола")
    zid_home: Mapped[Optional[int]] = mapped_column(BigInteger, comment="ZID дома")
    zid_work: Mapped[Optional[int]] = mapped_column(BigInteger, comment="ZID работы")

    # Quantities
    qnt_max: Mapped[Optional[int]] = mapped_column(
        Integer, comment="Максимальное количество"
    )
    qnt_traf: Mapped[Optional[int]] = mapped_column(
        Integer, comment="Количество трафика"
    )
    qnt_out: Mapped[Optional[int]] = mapped_column(
        Integer, comment="Количество исходящего"
    )

    # # Relationships
    # hour: Mapped[Optional["KaztelecomHour"]] = relationship(
    #     "KaztelecomHour", back_populates="mobile_data", lazy="selectin"
    # )
