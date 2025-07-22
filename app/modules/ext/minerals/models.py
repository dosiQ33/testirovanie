from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel
from datetime import date


class MineralsLocContracts(BasestModel):
    __tablename__ = "minerals_loc_contracts"
    __table_args__ = dict(schema="ext", comment="Минералс лицензии")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bin: Mapped[str] = mapped_column(comment="БИН")
    name: Mapped[str] = mapped_column(comment="Наименование")
    locnumber: Mapped[str] = mapped_column(comment="Номер лицензии")
    field_5: Mapped[str] = mapped_column()

    geom: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )

class IucMinerals(BasestModel):
    __tablename__ = "iuc_minerals"
    __table_args__ = dict(schema='ext')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    loc_number: Mapped[str] = mapped_column(name='loc_number', comment='Номер контракта', nullable=True)
    loc_date: Mapped[date] = mapped_column(name='loc_date', comment='Дата выдачи контракта', nullable=True)
    loc_type_id: Mapped[int] = mapped_column(ForeignKey('ext.iuc_loc_types.id'), comment='ID контракта')
    organization_id: Mapped[int] = mapped_column(ForeignKey('public.organizations.id'), comment='ID недропользователя')
    official_org_xin: Mapped[str] = mapped_column(name='official_org_xin', comment='БИН рабочего органа', nullable=True)
    official_org_name: Mapped[str] = mapped_column(name='official_org_name', comment='Наименование рабочего органа', nullable=True)
    loc_status: Mapped[str] = mapped_column(name='loc_status', comment='Статус лицензии', nullable=True)
    created_at: Mapped[date] = mapped_column(name='created_at', comment='Дата и время записи в БД', nullable=True)
    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Координаты",
        nullable=True,
    )

class IucLocTypes(BasestModel):
    __tablename__ = 'iuc_loc_types'
    __table_args__ = dict(schema='ext')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    loc_type: Mapped[str] = mapped_column(name='loc_type', comment='Тип контракта', nullable=True)