from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BaseModel

db_schema = "ckl"

def mapped_point_column() -> Mapped[WKBElement]:
    return mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Координаты",
        nullable=True,
    )

class Vehicles(BaseModel):
    __tablename__ = 'vehicles'
    __table_args__ = dict(schema=db_schema)


    number: Mapped[str] = mapped_column(name='number', comment='Государственный Регистрационный Номерной знак', nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicle_types.id'), comment='Тип ТС', nullable=False)
    make_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicle_makes.id'), comment='Марка ТС', nullable=False)
    shape: Mapped[int] = mapped_point_column()
    address: Mapped[str] = mapped_column(name='address', comment='Местоположения', nullable=True)
    kato_code: Mapped[str] = mapped_column(name='kato_code', comment='Код КАТО', nullable=True)
    rca_code: Mapped[str] = mapped_column(name='rca_code', comment='Код РКА', nullable=True)
    road_id: Mapped[int] = mapped_column(ForeignKey('ckl.roads.id'), comment='Дорога', nullable=False)
    year: Mapped[int] = mapped_column(name='year', comment='Год выпуска', nullable=True)
    vin_number: Mapped[str] = mapped_column(name='vin_number', comment='VIN-код (Уникальный номер шасси)', nullable=False)
    transport_company_id: Mapped[int] = mapped_column(ForeignKey('ckl.transport_companies.id'), comment='Компания-владелец', nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('ckl.countries.id'), comment='Страна регистрации', nullable=False)
    registration_date: Mapped[date] = mapped_column(name='registration_date', comment='Дата регистрации ТС', nullable=False)
    is_active: Mapped[bool] = mapped_column(name='is_active', comment='Активен/неактивен в системе', nullable=False)
    has_customs_booking: Mapped[bool] = mapped_column(name='has_customs_booking', comment='Наличие предварительного бронирования', nullable=False)

class Trailers(BaseModel):
    __tablename__ = 'trailers'
    __table_args__ = dict(schema=db_schema)

    number: Mapped[str] = mapped_column(name='number', comment='Номер прицепа, если есть', nullable=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicles.id'), comment='ТС', nullable=False)

class VehicleTypes(BaseModel):
    __tablename__ = 'vehicle_types'
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)


class VehicleMakes(BaseModel):
    __tablename__ = 'vehicle_makes'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код марки ТС', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)

class TransportCompanies(BaseModel):
    __tablename__ = 'transport_companies'
    __table_args__ = dict(schema=db_schema)

    is_international: Mapped[bool] = mapped_column(name='is_international', comment='Международная компания', nullable=False)
    bin: Mapped[str] = mapped_column(name='bin', comment='Бизнес-идентификационный номер', nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('public.organizations.id'), comment='Идентификатор организации', nullable=True)
    name: Mapped[str] = mapped_column(name='name', comment='Название компании', nullable=False)
    vat_number: Mapped[str] = mapped_column(name='vat_number', comment='Международный налоговый номер', nullable=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('ckl.countries.id'), comment='Код страны регистрации', nullable=True)
    registration_number: Mapped[str] = mapped_column(name='registration_number', comment='Регистрационный номер или номер лицензии', nullable=True)
    address: Mapped[str] = mapped_column(name='address', comment='Юридический или фактический адрес', nullable=True)
    phone: Mapped[str] = mapped_column(name='phone', comment='Телефон компании', nullable=True)
    email: Mapped[str] = mapped_column(name='email', comment='Электронная почта', nullable=True)
    contact_person: Mapped[str] = mapped_column(name='contact_person', comment='ФИО ответственного лица (например, диспетчер)', nullable=True)
    is_active: Mapped[bool] = mapped_column(name='is_active', comment='Признак активности компании', nullable=False)
