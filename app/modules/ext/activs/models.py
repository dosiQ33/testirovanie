from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datetime import date


from app.modules.common.models import BasestModel

class IucAlko(BasestModel):
    __tablename__ = 'iuc_alko_proizvod_temp'
    __table_args__ = dict(schema='ext')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(name='iin_bin', nullable=True)
    name_ru: Mapped[str] = mapped_column(name='name_ru', nullable=True)
    name_kz: Mapped[str] = mapped_column(name='name_kz', nullable=True)
    region: Mapped[str] = mapped_column(name="region", nullable=True)
    district: Mapped[str] = mapped_column(name="district", nullable=True)
    status: Mapped[str] = mapped_column(name="status", nullable=True)
    status_elicense: Mapped[str] = mapped_column(name="status_elicense", nullable=True)
    arc_code: Mapped[str] = mapped_column(name="arc_code", nullable=True)

    organization_id: Mapped[int] = mapped_column(ForeignKey('public.organizations.id'), nullable=False)

class IucNeftebasaCoordinatesTemp(BasestModel):
    __tablename__ = "iuc_neftebasa_coordinates_temp"
    __table_args__ =  dict(schema='ext')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(name="iin_bin", nullable=True)
    subject_name: Mapped[str] = mapped_column(name="subject_name", nullable=True)
    object_name: Mapped[str] = mapped_column(name="object_name", nullable=True)
    object_type: Mapped[str] = mapped_column(name="object_type", nullable=True)
    region: Mapped[str] = mapped_column(name="region", nullable=True)
    district: Mapped[str] = mapped_column(name="district", nullable=True)
    address: Mapped[str] = mapped_column(name="address", nullable=True)
    arc_code: Mapped[str] = mapped_column(name="arc_code", nullable=True)
    status: Mapped[str] = mapped_column(name="status", nullable=True)
    status_in_oiltrack: Mapped[str] = mapped_column(name="status_in_oiltrack", nullable=True)
    street_unique: Mapped[str] = mapped_column(name="street_unique", nullable=True)
    found_address: Mapped[str] = mapped_column(name="found_address", nullable=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("public.organizations.id"),
        nullable=False,
    )

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )

class IucAzsCoordinatesTemp(BasestModel):
    __tablename__ = "iuc_azs_coordinates_temp"
    __table_args__ =  dict(schema='ext')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(name="iin_bin", nullable=True)
    subject_name: Mapped[str] = mapped_column(name="subject_name", nullable=True)
    object_name: Mapped[str] = mapped_column(name="object_name", nullable=True)
    production_type: Mapped[str] = mapped_column(name="production_type", nullable=True)
    region: Mapped[str] = mapped_column(name="region", nullable=True)
    district: Mapped[str] = mapped_column(name="district", nullable=True)
    address: Mapped[str] = mapped_column(name="address", nullable=True)
    arc_code: Mapped[str] = mapped_column(name="arc_code", nullable=True)
    status: Mapped[str] = mapped_column(name="status", nullable=True)
    street_unique: Mapped[str] = mapped_column(name="street_unique", nullable=True)
    found_address: Mapped[str] = mapped_column(name="found_address", nullable=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("public.organizations.id"),
        nullable=False,
    )

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class IucNpzCoordinatesTemp(BasestModel):
    __tablename__ = "iuc_npz_coordinates_temp"
    __table_args__ =  dict(schema='ext')
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(name="iin_bin", nullable=True)
    subject_name: Mapped[str] = mapped_column(name="subject_name", nullable=True)
    object_name: Mapped[str] = mapped_column(name="object_name", nullable=True)
    object_type: Mapped[str] = mapped_column(name="object_type", nullable=True)
    region: Mapped[str] = mapped_column(name="region", nullable=True)
    district: Mapped[str] = mapped_column(name="district", nullable=True)
    address: Mapped[str] = mapped_column(name="address", nullable=True)
    arc_code: Mapped[str] = mapped_column(name="arc_code", nullable=True)
    status: Mapped[str] = mapped_column(name="status", nullable=True)
    street_unique: Mapped[str] = mapped_column(name="street_unique", nullable=True)
    found_address: Mapped[str] = mapped_column(name="found_address", nullable=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("public.organizations.id"),
        nullable=False,
    )

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )


class IucZernoCoordinatesTemp(BasestModel):
    __tablename__ = "iuc_zerno_coordinates_temp"
    __table_args__ = {"schema": "ext"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(name="iin_bin", nullable=True)
    subject_name: Mapped[str] = mapped_column(name="subject_name", nullable=True)
    region: Mapped[str] = mapped_column(name="region", nullable=True)
    district: Mapped[str] = mapped_column(name="district", nullable=True)
    address: Mapped[str] = mapped_column(name="address", nullable=True)
    status: Mapped[str] = mapped_column(name="status", nullable=True)
    granary_capacity_tons: Mapped[str] = mapped_column(name="granary_capacity_tons", nullable=True)
    load_capacity_tons: Mapped[str] = mapped_column(name="load_capacity_tons", nullable=True)
    arc_code: Mapped[str] = mapped_column(name="arc_code", nullable=True)
    street_unique: Mapped[str] = mapped_column(name="street_unique", nullable=True)
    coordinates: Mapped[str] = mapped_column(name="coordinates", nullable=True)
    found_address: Mapped[str] = mapped_column(name="found_address", nullable=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("public.organizations.id"),
        nullable=False,
    )

    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )