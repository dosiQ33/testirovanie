from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel, BaseModel
from datetime import date, datetime

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

class RoadServices(BasestModel):
    __tablename__ = 'road_services'
    __table_args__ = dict(schema=db_schema)
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    segment_index: Mapped[str] = mapped_column(name='segment_index', comment='Индекс / код платного участка', nullable=True)
    toll_section: Mapped[bool] = mapped_column(name='toll_section', comment='Признак «Платный участок» (да/нет)', nullable=True)
    road_id: Mapped[int] = mapped_column(ForeignKey('ckl.roads.id'), comment='Наименование дороги', nullable=True)
    km_mark: Mapped[str] = mapped_column(name='km_mark', comment='Километр (точка размещения объекта)', nullable=True)
    placement_side: Mapped[str] = mapped_column(name='placement_side', comment='Расположение (справа/слева)', nullable=True)
    reverse_km_mark: Mapped[str] = mapped_column(name='reverse_km_mark', comment='Обратный километраж (км)', nullable=True)
    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )
    service_name: Mapped[str] = mapped_column(name='service_name', comment='Наименование сервиса (АЗС, кафе, мотель и т.п.)', nullable=True)
    owner_name: Mapped[str] = mapped_column(name='owner_name', comment='Владельцы / ФИО ОПС', nullable=True)
    owner_contact: Mapped[str] = mapped_column(name='owner_contact', comment='Контактные данные владельцев', nullable=True)
    ods_category: Mapped[str] = mapped_column(name='ods_category', comment='Категория ОДС согласно нац. стандарту', nullable=True)
    standard_compliance: Mapped[bool] = mapped_column(name='standard_compliance', comment='Соответствие нац. стандарту (да/нет)', nullable=True)
    commissioning_year: Mapped[int] = mapped_column(name='commissioning_year', comment='Год ввода объекта', nullable=True)
    land_allocation: Mapped[bool] = mapped_column(name='land_allocation', comment='Признак отвода земли', nullable=True)
    engineering_networks: Mapped[bool] = mapped_column(name='engineering_networks', comment='Наличие инженерных сетей', nullable=True)
    exits: Mapped[bool] = mapped_column(name='exits', comment='Наличие съездов/въездов', nullable=True)
    fuel_station: Mapped[bool] = mapped_column(name='fuel_station', comment='Автозаправочные станции', nullable=True)
    motel: Mapped[bool] = mapped_column(name='motel', comment='Мотель', nullable=True)
    toilet: Mapped[bool] = mapped_column(name='toilet', comment='Благоустроенный санузел', nullable=True)
    food_point: Mapped[bool] = mapped_column(name='food_point', comment='Пункт питания', nullable=True)
    retail_point: Mapped[bool] = mapped_column(name='retail_point', comment='Пункт розничной торговли', nullable=True)
    showers: Mapped[bool] = mapped_column(name='showers', comment='Душевые кабины', nullable=True)
    service_station: Mapped[bool] = mapped_column(name='service_station', comment='СТО (станция техобслуживания)', nullable=True)
    car_wash: Mapped[bool] = mapped_column(name='car_wash', comment='Автомойка', nullable=True)
    medical_point: Mapped[bool] = mapped_column(name='medical_point', comment='Пункт медицинской помощи', nullable=True)
    parking: Mapped[bool] = mapped_column(name='parking', comment='Стоянка', nullable=True)
    guarded_parking: Mapped[bool] = mapped_column(name='guarded_parking', comment='Охраняемая стоянка', nullable=True)
    entertainment_zone: Mapped[bool] = mapped_column(name='entertainment_zone', comment='Торгово-развлекательная зона', nullable=True)
    picnic_area: Mapped[bool] = mapped_column(name='picnic_area', comment='Место для пикника', nullable=True)
    accessible_facilities: Mapped[bool] = mapped_column(name='accessible_facilities', comment='Удобства для маломобильных граждан (пандус, поручни и т.п.)', nullable=True)
    video_surveillance: Mapped[bool] = mapped_column(name='video_surveillance', comment='Видеонаблюдение', nullable=True)
    region: Mapped[str] = mapped_column(name='region', comment='Область расположения', nullable=True)

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

class CameraEvents(BaseModel):
    __tablename__ = 'camera_events'
    __table_args__ = dict(schema=db_schema)

    vehicle_id: Mapped[int] = mapped_column(ForeignKey('ckl.vehicles.id'), comment='Транспортное средство', nullable=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey('ckl.cameras.id'), comment='Ссылка на камеру', nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(name='event_timestamp', comment='Дата и время фиксации события', nullable=False)
    shape: Mapped[int] = mapped_column(name='shape', comment='Координаты GPS', nullable=False)
    address: Mapped[str] = mapped_column(name='address', comment='Местоположения', nullable=True)
    speed: Mapped[float] = mapped_column(name='speed', comment='Скорость автомобиля в момент фиксации', nullable=False)
    image_url: Mapped[str] = mapped_column(name='image_url', comment='Ссылка на изображение', nullable=True)
    is_recognized: Mapped[bool] = mapped_column(name='is_recognized', comment='Было ли успешно распознано ТС', nullable=True)
    comments: Mapped[str] = mapped_column(name='comments', comment='Примечания', nullable=True)
