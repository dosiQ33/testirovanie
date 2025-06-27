from __future__ import annotations
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BaseModel
# from app.modules.main.models import Organizations, RiskInfos


class DAtsTypes(BaseModel):
    __tablename__ = "d_ats_types"
    __table_args__ = dict(schema="ar", comment="Типы административно-территориальных единиц")

    code: Mapped[int] = mapped_column(comment="Код")
    value_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    value_ru: Mapped[str] = mapped_column(comment="Наименование РУС")
    short_value_kz: Mapped[str] = mapped_column(comment="Краткое наименование КАЗ", nullable=True)
    short_value_ru: Mapped[str] = mapped_column(comment="Краткое наименование РУС", nullable=True)
    actual: Mapped[bool] = mapped_column(comment="Действующее")


class DBuildingsPointers(BaseModel):
    __tablename__ = "d_buildings_pointers"
    __table_args__ = dict(schema="ar", comment="Указатели типов первичных объектов недвижимости")

    code: Mapped[int] = mapped_column(comment="Код")
    value_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    value_ru: Mapped[str] = mapped_column(comment="Наименование РУС")
    short_value_kz: Mapped[str] = mapped_column(comment="Краткое наименование КАЗ", nullable=True)
    short_value_ru: Mapped[str] = mapped_column(comment="Краткое наименование РУС", nullable=True)
    actual: Mapped[bool] = mapped_column(comment="Действующее")


class DGeonimsTypes(BaseModel):
    __tablename__ = "d_geonims_types"
    __table_args__ = dict(schema="ar", comment="Типы составных частей населенных пунктов")

    code: Mapped[int] = mapped_column(comment="Код")
    value_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    value_ru: Mapped[str] = mapped_column(comment="Наименование РУС")
    short_value_kz: Mapped[str] = mapped_column(comment="Краткое наименование КАЗ", nullable=True)
    short_value_ru: Mapped[str] = mapped_column(comment="Краткое наименование РУС", nullable=True)
    actual: Mapped[bool] = mapped_column(comment="Действующее")
    this_is: Mapped[str] = mapped_column(comment="Дорога", nullable=True)


class DRoomsTypes(BaseModel):
    __tablename__ = "d_rooms_types"
    __table_args__ = dict(schema="ar", comment="Типы помещений")

    code: Mapped[int] = mapped_column(comment="Код")
    value_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    value_ru: Mapped[str] = mapped_column(comment="Наименование РУС")
    short_value_kz: Mapped[str] = mapped_column(comment="Краткое наименование КАЗ", nullable=True)
    short_value_ru: Mapped[str] = mapped_column(comment="Краткое наименование РУС", nullable=True)
    actual: Mapped[bool] = mapped_column(comment="Действующее")


class SAts(BaseModel):
    __tablename__ = "s_ats"
    __table_args__ = dict(schema="ar", comment="Административно-территориальные единицы")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_ats.id"), comment="Родитель", nullable=True)
    parent: Mapped["SAts"] = relationship("SAts", lazy="selectin", join_depth=10)

    name_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    name_ru: Mapped[str] = mapped_column(comment="Наименование РУС")

    rco: Mapped[Optional[str]] = mapped_column(comment="Код РКО", nullable=True)
    cato: Mapped[Optional[str]] = mapped_column(comment="Код КАТО", nullable=True)

    d_ats_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.d_ats_types.id"), comment="Тип АТЕ", nullable=True)
    d_ats_type: Mapped["DAtsTypes"] = relationship("DAtsTypes", lazy="selectin")

    actual: Mapped[bool] = mapped_column(comment="Действующее")

    # Служебные поля
    full_address_ru: Mapped[Optional[str]] = mapped_column(comment="Полный адрес РУС", nullable=True)
    full_address_kz: Mapped[Optional[str]] = mapped_column(comment="Полный адрес КАЗ", nullable=True)
    path: Mapped[Optional[JSONB]] = mapped_column(type_=JSONB, comment="Полный путь", nullable=True)
    is_leaf: Mapped[bool] = mapped_column(comment="Крайний элемент", default=False)

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class SGeonims(BaseModel):
    __tablename__ = "s_geonims"
    __table_args__ = dict(schema="ar", comment="Части АТЕ")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_geonims.id"), comment="Родитель", nullable=True)
    parent: Mapped["SGeonims"] = relationship("SGeonims", lazy="selectin", join_depth=10)

    name_kz: Mapped[str] = mapped_column(comment="Наименование КАЗ")
    name_ru: Mapped[str] = mapped_column(comment="Наименование РУС")

    rco: Mapped[Optional[str]] = mapped_column(comment="Код РКО", nullable=True)
    cato: Mapped[Optional[str]] = mapped_column(comment="Код КАТО", nullable=True)

    s_ats_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_ats.id"), comment="АТЕ", nullable=True)
    s_ats: Mapped["SAts"] = relationship("SAts", lazy="selectin")

    d_geonims_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.d_geonims_types.id"), comment="Тип", nullable=True)
    d_geonims_type: Mapped["DGeonimsTypes"] = relationship("DGeonimsTypes", lazy="selectin")

    actual: Mapped[bool] = mapped_column(comment="Действующее")

    # Служебные поля
    full_address_ru: Mapped[Optional[str]] = mapped_column(comment="Полный адрес РУС", nullable=True)
    full_address_kz: Mapped[Optional[str]] = mapped_column(comment="Полный адрес КАЗ", nullable=True)
    path: Mapped[Optional[JSONB]] = mapped_column(type_=JSONB, comment="Полный путь", nullable=True)
    is_leaf: Mapped[bool] = mapped_column(comment="Крайний элемент", default=False)

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class SGrounds(BaseModel):
    __tablename__ = "s_grounds"
    __table_args__ = dict(schema="ar", comment="Земельные участки")

    s_ats_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_ats.id"), comment="АТЕ", nullable=True)
    s_ats: Mapped["SAts"] = relationship("SAts", lazy="selectin")

    s_geonim_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_geonims.id"), comment="Часть АТЕ", nullable=True)
    s_geonim: Mapped["SGeonims"] = relationship("SGeonims", lazy="selectin")

    rca: Mapped[Optional[str]] = mapped_column(comment="Регистрационный код адреса", nullable=True)
    number: Mapped[Optional[str]] = mapped_column(comment="Номер участка", nullable=True)
    cadastre_number: Mapped[Optional[str]] = mapped_column(comment="Кадастровый номер", nullable=True)

    actual: Mapped[bool] = mapped_column(comment="Действующее")

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class SBuildings(BaseModel):
    __tablename__ = "s_buildings"
    __table_args__ = dict(schema="ar", comment="Первичные объекты адресации (здания)")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_buildings.id"), comment="Родитель", nullable=True)
    parent: Mapped["SBuildings"] = relationship("SBuildings", lazy="selectin", join_depth=10)

    name_kz: Mapped[Optional[str]] = mapped_column(comment="Наименование КАЗ", nullable=True)
    name_ru: Mapped[Optional[str]] = mapped_column(comment="Наименование РУС", nullable=True)

    s_ats_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_ats.id"), comment="АТЕ", nullable=True)
    s_ats: Mapped["SAts"] = relationship("SAts", lazy="selectin")

    s_geonim_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_geonims.id"), comment="Часть АТЕ", nullable=True)
    s_geonim: Mapped["SGeonims"] = relationship("SGeonims", lazy="selectin")

    d_buildings_pointer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ar.d_buildings_pointers.id"), comment="Тип", nullable=True
    )
    d_buildings_pointer: Mapped["DBuildingsPointers"] = relationship("DBuildingsPointers", lazy="selectin")

    rca: Mapped[Optional[str]] = mapped_column(comment="Регистрационный код адреса", nullable=True)
    number: Mapped[Optional[str]] = mapped_column(comment="Номер объекта", nullable=True)
    distance: Mapped[Optional[float]] = mapped_column(comment="Расстояние от начала дороги (км)", default=0)
    this_is: Mapped[Optional[str]] = mapped_column(comment="Подтип", nullable=True)

    actual: Mapped[bool] = mapped_column(comment="Действующее")

    # Служебные поля
    full_address_ru: Mapped[Optional[str]] = mapped_column(comment="Полный адрес РУС", nullable=True)
    full_address_kz: Mapped[Optional[str]] = mapped_column(comment="Полный адрес КАЗ", nullable=True)
    path: Mapped[Optional[JSONB]] = mapped_column(type_=JSONB, comment="Полный путь", nullable=True)
    path_names_ru: Mapped[Optional[List[str]]] = mapped_column(
        type_=ARRAY(String), comment="Полный путь названий РУС", nullable=True
    )
    path_names_kz: Mapped[Optional[List[str]]] = mapped_column(
        type_=ARRAY(String), comment="Полный путь названий РУС", nullable=True
    )

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class SPb(BaseModel):
    __tablename__ = "s_pb"
    __table_args__ = dict(schema="ar", comment="Вторичные объекты адресации (помещения)")

    s_building_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.s_buildings.id"), comment="Здание", nullable=True)
    s_building: Mapped["SBuildings"] = relationship("SBuildings", lazy="selectin")

    d_room_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ar.d_rooms_types.id"), comment="Тип", nullable=True)
    d_room_type: Mapped["DRoomsTypes"] = relationship("DRoomsTypes", lazy="selectin")

    rca: Mapped[Optional[str]] = mapped_column(comment="Регистрационный код адреса", nullable=True)
    number: Mapped[Optional[str]] = mapped_column(comment="Номер помещения", nullable=True)

    actual: Mapped[bool] = mapped_column(comment="Действующее")

    # Служебные поля
    full_address_ru: Mapped[Optional[str]] = mapped_column(comment="Полный адрес РУС", nullable=True)
    full_address_kz: Mapped[Optional[str]] = mapped_column(comment="Полный адрес КАЗ", nullable=True)
