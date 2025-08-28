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

class Warehouses(BaseModel):
    __tablename__ = 'warehouses'
    __table_args__ = dict(schema=db_schema)

    vehicle_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicles.id'), comment='Ссылка на ТС', nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('ckl.warehouse_types.id'), comment='Тип склада', nullable=True)
    name: Mapped[str] = mapped_column(name='name', comment='Название склада', nullable=False)
    shape: Mapped[int] = mapped_column(name='shape', comment='GPS-координаты', nullable=False)
    address: Mapped[str] = mapped_column(name='address', comment='Адрес или описание местоположения', nullable=True)
    kato_code: Mapped[str] = mapped_column(name='kato_code', comment='Регион или административная зона', nullable=True)
    rca_code: Mapped[str] = mapped_column(name='rca_code', comment='Код РКА', nullable=True)
    capacity_m3: Mapped[float] = mapped_column(name='capacity_m3', comment='Вместимость склада в кубических метрах', nullable=False)
    contact_person: Mapped[str] = mapped_column(name='contact_person', comment='Ответственное лицо или оператор', nullable=False)
    phone: Mapped[str] = mapped_column(name='phone', comment='Контактный телефон', nullable=False)
    is_active: Mapped[bool] = mapped_column(name='is_active', comment='Признак активности склада', nullable=False)

class WeighStationTypes(BaseModel):
    __tablename__ = 'weigh_station_types'
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)

class WeighStations(BaseModel):
    __tablename__ = 'weigh_stations'
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str] = mapped_column(name='code', comment='Код станции', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Название станции на казахском языке', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Название станции на русском языке', nullable=False)
    shape: Mapped[int] = mapped_column(name='shape', comment='GPS-координаты', nullable=False)
    address: Mapped[str] = mapped_column(name='address', comment='Местоположения', nullable=True)
    kato_code: Mapped[str] = mapped_column(name='kato_code', comment='Код КАТО', nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('ckl.weigh_station_types.id'), comment='Тип станции', nullable=True)
    has_camera: Mapped[bool] = mapped_column(name='has_camera', comment='Имеет камеру фиксации', nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey('ckl.cameras.id'), comment='Камера', nullable=True)
    is_active: Mapped[bool] = mapped_column(name='is_active', comment='Активна ли станция', nullable=False)
    weigh_stations_operator_id: Mapped[int] = mapped_column(ForeignKey('ckl.weigh_stations_operators.id'), comment='Организация/подразделение, обслуживающее станцию', nullable=True)
    installation_date: Mapped[date] = mapped_column(name='installation_date', comment='Дата ввода станции в эксплуатацию', nullable=False)

class WeighStationsOperators(BaseModel):
    __tablename__ = 'weigh_stations_operators'
    __table_args__ = dict(schema=db_schema)

    iin_bin: Mapped[str] = mapped_column(name='iin_bin', comment='ИИН/БИН оператора камер', nullable=False)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование на русском языке', nullable=False)
    name_kk: Mapped[str] = mapped_column(name='name_kk', comment='Наименование на казахском языке', nullable=False)

class WeighingEvents(BaseModel):
    __tablename__ = 'weighing_events'
    __table_args__ = dict(schema=db_schema)

    vehicle_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicles.id'), comment='Транспортное средство', nullable=False)
    weigh_station_id: Mapped[int] = mapped_column(ForeignKey('ckl.weigh_stations.id'), comment='Станция весового контроля', nullable=False)
    event_timespamp: Mapped[datetime] = mapped_column(name='event_timespamp', comment='Дата и время взвешивания', nullable=False)
    gross_weight_kg: Mapped[float] = mapped_column(name='gross_weight_kg', comment='Общий вес ТС с грузом, кг', nullable=False)
    tare_weight_kg: Mapped[float] = mapped_column(name='tare_weight_kg', comment='Вес пустого автомобиля (если есть)', nullable=False)
    net_weight_kg: Mapped[float] = mapped_column(name='net_weight_kg', comment='Вес груза, кг (расчетный или измеренный)', nullable=False)
    allowed_weight_kg: Mapped[float] = mapped_column(name='allowed_weight_kg', comment='Допустимый максимальный вес', nullable=False)
    is_overload: Mapped[bool] = mapped_column(name='is_overload', comment='Превышен допустимый вес', nullable=False)
    overload_kg: Mapped[float] = mapped_column(name='overload_kg', comment='Величина перегруза (если есть)', nullable=True)
    operator_name: Mapped[str] = mapped_column(name='operator_name', comment='Имя оператора', nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey('ckl.cameras.id'), comment='Камера, фиксирующая взвешивание', nullable=True)
    image_url: Mapped[str] = mapped_column(name='image_url', comment='Ссылка на изображение автомобиля', nullable=True)
    comments: Mapped[str] = mapped_column(name='comments', comment='Примечания/комментарии', nullable=True)