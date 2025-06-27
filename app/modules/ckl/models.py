from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class Countries(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Страны")
    name: Mapped[str] = mapped_column(comment="Название страны", nullable=False)
    code: Mapped[str] = mapped_column(comment="Код страны", nullable=False)


class CustomsOffices(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Таможенные органы")
    code: Mapped[str] = mapped_column(comment="Код", nullable=False)
    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class CustomsProcedures(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Таможенные процедуры")
    name: Mapped[str] = mapped_column(comment="Наименование таможенной процедуры", nullable=False)


class CustomsPoints(BaseModel):
    # __tablename__ = "customs_points"
    __table_args__ = dict(schema=db_schema, comment="Пункты пропуска через границу")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    country_border: Mapped[str] = mapped_column(comment="Название границы", nullable=False)
    location_name: Mapped[str] = mapped_column(comment="Название пункта", nullable=False)
    location_address: Mapped[str] = mapped_column(comment="Адрес ППГ", nullable=False)
    location_coords: Mapped[WKBElement] = mapped_point_column()


class TransportCompanies(BaseModel):
    # __tablename__ = "transport_companies"
    __table_args__ = dict(schema=db_schema, comment="Транспортные компании")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    bin: Mapped[str] = mapped_column(comment="БИН", nullable=True)
    is_international: Mapped[bool] = mapped_column(comment="Международная компания", nullable=False)
    vat_number: Mapped[str] = mapped_column(comment="Международный налоговый номер", nullable=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна", nullable=False)
    country: Mapped["Countries"] = relationship("Countries", lazy="selectin")
    registration_number: Mapped[str] = mapped_column(comment="Регистрационный номер или номер лицензии", nullable=False)
    address: Mapped[str] = mapped_column(comment="Юридический или фактический адрес", nullable=False)
    phone: Mapped[str] = mapped_column(comment="Телефон", nullable=False)
    email: Mapped[str] = mapped_column(comment="Электронная почта", nullable=True)
    contact_person: Mapped[str] = mapped_column(comment="Контактное лицо", nullable=True)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class VehicleTypes(BaseModel):
    # __tablename__ = "vehicle_types"
    __table_args__ = dict(schema=db_schema, comment="Типы транспортных средств")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class VehicleMakeTypes(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Марки транспортных средств")
    code: Mapped[int] = mapped_column(comment="Код", nullable=False)
    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class Vehicles(BaseModel):
    # __tablename__ = "vehicles"
    __table_args__ = dict(schema=db_schema, comment="Транспортные средства")

    number: Mapped[str] = mapped_column(comment="Номер", nullable=False)
    trailer_number: Mapped[str] = mapped_column(comment="Номер прицепа", nullable=True)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicle_types.id"),
        comment="Тип транспортного средства",
        nullable=False,
    )
    type: Mapped["VehicleTypes"] = relationship("VehicleTypes", lazy="selectin")
    make_id: Mapped[int] = mapped_column(ForeignKey("ckl.vehicle_make_types.id"), comment="Марка", nullable=False)
    make: Mapped["VehicleMakeTypes"] = relationship("VehicleMakeTypes", lazy="selectin")
    year: Mapped[int] = mapped_column(comment="Год выпуска", nullable=True)
    vin_number: Mapped[str] = mapped_column(comment="VIN код", nullable=False)
    transport_company_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.transport_companies.id"),
        comment="Транспортная компания",
        nullable=False,
    )
    transport_company: Mapped["TransportCompanies"] = relationship("TransportCompanies", lazy="selectin")
    country_registration: Mapped[str] = mapped_column(comment="Страна регистрации", nullable=False)
    registration_date: Mapped[date] = mapped_column(comment="Дата регистрации", nullable=False)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)

    location_gps: Mapped[WKBElement] = mapped_point_column()
    location_text: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=True)
    location_timestamp: Mapped[datetime] = mapped_column(comment="Время фиксации положения", nullable=True)


class BookingStatuses(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Статусы бронирования")
    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class Bookings(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Бронирования")
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("ckl.vehicles.id"), comment="ТС", nullable=True)
    driver_name: Mapped[str] = mapped_column(comment="ФИО водителя", nullable=True)
    driver_phone: Mapped[str] = mapped_column(comment="Контактный номер водителя", nullable=True)
    customs_point_id: Mapped[int] = mapped_column(ForeignKey("ckl.customs_points.id"), comment="Таможенный пост", nullable=True)
    booking_date: Mapped[date] = mapped_column(comment="Дата бронирования", nullable=True)
    entry_datetime: Mapped[datetime] = mapped_column(comment="Желаемое время прибытия", nullable=True)
    is_exit: Mapped[bool] = mapped_column(comment="Въезд-Выезд", nullable=False)
    booking_status_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.booking_statuses.id"),
        comment="Статус бронирования",
        nullable=True,
    )
    is_inspection_required: Mapped[bool] = mapped_column(comment="Требуется ли досмотр", nullable=True)
    document_number: Mapped[str] = mapped_column(comment="Номер сопроводительного документа", nullable=True)
    comments: Mapped[str] = mapped_column(Text, comment="Дополнительная информация или примечания", nullable=False)


class CameraTypes(BaseModel):
    # __tablename__ = "camera_types"
    __table_args__ = dict(schema=db_schema, comment="Типы камер")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class Cameras(BaseModel):
    # __tablename__ = "cameras"
    __table_args__ = dict(schema=db_schema, comment="Камеры")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("ckl.camera_types.id"), comment="Тип камеры", nullable=False)
    type: Mapped["CameraTypes"] = relationship("CameraTypes", lazy="selectin")
    shape: Mapped[WKBElement] = mapped_point_column()
    location_text: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=False)
    direction_supported: Mapped[str] = mapped_column(comment="Поддерживаемые направления", nullable=False)
    operator_name: Mapped[str] = mapped_column(comment="Кем обслуживается", nullable=False)
    installation_date: Mapped[date] = mapped_column(comment="Дата установки", nullable=False)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class CameraEvents(BaseModel):
    # __tablename__ = "camera_events"
    __table_args__ = dict(schema=db_schema, comment="События камер")

    camera_id: Mapped[int] = mapped_column(ForeignKey("ckl.cameras.id"), comment="Камера", nullable=False)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicles.id"),
        comment="Транспортное средство",
        nullable=False,
    )
    # vehicle: Mapped["Vehicles"] = relationship("Vehicles", lazy="selectin")
    speed: Mapped[float] = mapped_column(comment="Скорость автомобиля в момент фиксации", nullable=False)
    direction: Mapped[str] = mapped_column(comment="Направление движения", nullable=False)
    image_url: Mapped[str] = mapped_column(comment="URL изображения", nullable=False)
    is_recognized: Mapped[bool] = mapped_column(comment="Было ли успешно распознано ТС", nullable=False)
    remarks: Mapped[str] = mapped_column(Text, comment="Комментарии", nullable=True)


class WeightingStations(BaseModel):
    # __tablename__ = "weighting_stations"
    __table_args__ = dict(schema=db_schema, comment="Весовые станции")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    location_coords: Mapped[WKBElement] = mapped_point_column()
    location_text: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=False)
    region: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=False)
    type: Mapped[str] = mapped_column(comment="Тип станции", nullable=False)
    has_camera: Mapped[bool] = mapped_column(comment="Имеет камеру фиксации", nullable=False)
    operator_name: Mapped[str] = mapped_column(comment="Кем обслуживается", nullable=False)
    installation_date: Mapped[date] = mapped_column(comment="Дата установки", nullable=False)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class WeightingEvents(BaseModel):
    # __tablename__ = "weighting_events"
    __table_args__ = dict(schema=db_schema, comment="События весовых станций")

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicles.id"),
        comment="Транспортное средство",
        nullable=False,
    )
    # vehicle: Mapped["Vehicles"] = relationship("Vehicles", lazy="selectin")
    weighting_station_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.weighting_stations.id"),
        comment="Весовая станция",
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(comment="Дата-Время взвешивания", nullable=False)
    gross_weight_kg: Mapped[float] = mapped_column(comment="Общий вес ТС с грузом, кг", nullable=False)
    tare_weight_kg: Mapped[float] = mapped_column(comment="Вес ТС без груза, кг", nullable=False)
    net_weight_kg: Mapped[float] = mapped_column(comment="Вес груза, кг", nullable=False)
    allowed_weight_kg: Mapped[float] = mapped_column(comment="Допустимый максимальный вес, кг", nullable=False)
    is_overload: Mapped[bool] = mapped_column(comment="Перегруз", nullable=False)
    overload_kg: Mapped[float] = mapped_column(comment="Перегруз, кг", nullable=False)
    operator_name: Mapped[str] = mapped_column(comment="Имя оператора или системы", nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey("ckl.cameras.id"), comment="Камера", nullable=True)
    image_url: Mapped[str] = mapped_column(comment="URL изображения", nullable=True)
    remarks: Mapped[str] = mapped_column(Text, comment="Комментарии", nullable=True)


class Senders(BaseModel):
    # __tablename__ = "senders"
    __table_args__ = dict(schema=db_schema, comment="Отправители")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    iin_bin: Mapped[str] = mapped_column(comment="ИИН/БИН", nullable=True)
    is_foreign: Mapped[bool] = mapped_column(comment="Иностранный отправитель", nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна", nullable=False)
    country: Mapped["Countries"] = relationship("Countries", lazy="selectin")
    address: Mapped[str] = mapped_column(comment="Адрес", nullable=False)
    phone: Mapped[str] = mapped_column(comment="Телефон", nullable=False)
    email: Mapped[str] = mapped_column(comment="Электронная почта", nullable=True)
    contact_person: Mapped[str] = mapped_column(comment="Контактное лицо", nullable=True)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class Receivers(BaseModel):
    # __tablename__ = "receivers"
    __table_args__ = dict(schema=db_schema, comment="Получатели")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    iin_bin: Mapped[str] = mapped_column(comment="ИИН/БИН", nullable=True)
    is_foreign: Mapped[bool] = mapped_column(comment="Иностранный получатель", nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна", nullable=False)
    country: Mapped["Countries"] = relationship("Countries", lazy="selectin")
    address: Mapped[str] = mapped_column(comment="Адрес", nullable=False)
    phone: Mapped[str] = mapped_column(comment="Телефон", nullable=False)
    email: Mapped[str] = mapped_column(comment="Электронная почта", nullable=True)
    contact_person: Mapped[str] = mapped_column(comment="Контактное лицо", nullable=True)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class CustomsDeclarations(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="ГТД")

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicles.id"),
        comment="Уникальный идентификатор ТС",
        nullable=True,
    )
    number: Mapped[str] = mapped_column(comment="Номер грузовой таможенной декларации (ГТД)", nullable=True)
    accompanying_docs: Mapped[str] = mapped_column(Text, comment="Список сопровождающих документов", nullable=True)
    customs_office_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_offices.id"),
        comment="Таможенный орган оформления",
        nullable=True,
    )
    declaration_date: Mapped[date] = mapped_column(comment="Дата регистрации декларации", nullable=True)
    status_id: Mapped[int] = mapped_column(comment="Статус декларации", nullable=True)
    customs_procedure_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_procedures.id"),
        comment="Код таможенной процедуры",
        nullable=True,
    )
    exporter_bin: Mapped[str] = mapped_column(comment="БИН экспортёра", nullable=True)
    importer_bin: Mapped[str] = mapped_column(comment="БИН импортёра (резидента РК)", nullable=True)

    origin_country_id: Mapped[int] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна происхождения", nullable=False)
    origin_country: Mapped["Countries"] = relationship(
        "Countries", lazy="selectin", foreign_keys="CustomsDeclarations.origin_country_id"
    )

    registration_country_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.countries.id"), comment="Страна регистрации", nullable=False
    )
    registration_country: Mapped["Countries"] = relationship(
        "Countries", lazy="selectin", foreign_keys="CustomsDeclarations.registration_country_id"
    )

    departure_country_id: Mapped[int] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна отправления", nullable=True)
    departure_country: Mapped["Countries"] = relationship(
        "Countries", lazy="selectin", foreign_keys="CustomsDeclarations.departure_country_id"
    )

    destination_country_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.countries.id"), comment="Страна назначения", nullable=True
    )
    destination_country: Mapped["Countries"] = relationship(
        "Countries", lazy="selectin", foreign_keys="CustomsDeclarations.destination_country_id"
    )

    border_crossing_point_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.border_crossing_points.id"),
        comment="Пункт пересечения границы",
        nullable=True,
    )
    release_date: Mapped[datetime] = mapped_column(comment="Дата выпуска товара в свободное обращение", nullable=True)
    total_invoice_amount: Mapped[float] = mapped_column(comment="Общая стоимость по инвойсу (в валюте контракта)", nullable=True)
    contract_currency: Mapped[str] = mapped_column(comment="Валюта контракта (ISO 4217)", nullable=True)
    total_customs_value: Mapped[float] = mapped_column(comment="Таможенная стоимость", nullable=True)
    duty_amount: Mapped[float] = mapped_column(comment="Сумма начисленных пошлин", nullable=True)
    vat_amount: Mapped[float] = mapped_column(comment="Сумма начисленного НДС", nullable=True)
    excise_amount: Mapped[float] = mapped_column(comment="Сумма акциза", nullable=True)
    declaration_type_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.declaration_types.id"),
        comment="Тип декларации",
        nullable=True,
    )
    item_id: Mapped[int] = mapped_column(comment="Ссылка на товар", nullable=True)
    invoice_value: Mapped[float] = mapped_column(comment="Стоимость по инвойсу", nullable=True)
    customs_value: Mapped[float] = mapped_column(comment="Таможенная стоимость", nullable=True)
    duty_rate: Mapped[float] = mapped_column(comment="Ставка пошлины", nullable=True)
    vat_rate: Mapped[float] = mapped_column(comment="Ставка НДС", nullable=True)

    participant_id: Mapped[int] = mapped_column(comment="Уникальный ID участника", nullable=True)
    role_id: Mapped[int] = mapped_column(comment="Роль (exporter/importer/carrier)", nullable=True)
    participant_bin: Mapped[str] = mapped_column(comment="Идентификационный номер участника (БИН)", nullable=True)
    participant_name: Mapped[str] = mapped_column(comment="Наименование участника", nullable=True)

    address: Mapped[str] = mapped_column(Text, comment="Адрес регистрации", nullable=True)
    created_at: Mapped[datetime] = mapped_column(comment="Дата создания записи", nullable=True)
    updated_at: Mapped[datetime] = mapped_column(comment="Дата последнего обновления", nullable=True)


class Inspections(BaseModel):
    # __tablename__ = "inspections"
    __table_args__ = dict(schema=db_schema, comment="Проверки")

    type: Mapped[str] = mapped_column(comment="Тип досмотра", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(comment="Дата-Время досмотра", nullable=False)
    inspector: Mapped[str] = mapped_column(comment="ФИО/ID инспектора", nullable=False)
    result: Mapped[str] = mapped_column(Text, comment="Результат досмотра", nullable=False)


class CargoTypes(BaseModel):
    # __tablename__ = "cargo_types"
    __table_args__ = dict(schema=db_schema, comment="Типы грузов")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class PackageTypes(BaseModel):
    # __tablename__ = "package_types"
    __table_args__ = dict(schema=db_schema, comment="Типы упаковки")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)


class Cargos(BaseModel):
    # __tablename__ = "cargos"
    __table_args__ = dict(schema=db_schema, comment="Грузы")

    customs_declaration_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_declarations.id"),
        comment="Накладная",
        nullable=False,
    )
    customs_declaration: Mapped["CustomsDeclarations"] = relationship("CustomsDeclarations", lazy="selectin")

    description: Mapped[str] = mapped_column(comment="Описание груза", nullable=False)
    cargo_type_id: Mapped[int] = mapped_column(ForeignKey("ckl.cargo_types.id"), comment="Тип груза", nullable=False)
    cargo_type: Mapped["CargoTypes"] = relationship("CargoTypes", lazy="selectin")
    weight_kg: Mapped[float] = mapped_column(comment="Вес груза в кг", nullable=False)
    volume_m3: Mapped[float] = mapped_column(comment="Объем груза в м3", nullable=False)
    package_type_id: Mapped[int] = mapped_column(ForeignKey("ckl.package_types.id"), comment="Тип упаковки", nullable=False)
    temperature_mode: Mapped[str] = mapped_column(comment="Температурный режим", nullable=True)
    is_dangerous: Mapped[bool] = mapped_column(comment="Опасный груз", nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("ckl.senders.id"), comment="Отправитель", nullable=False)
    sender: Mapped["Senders"] = relationship("Senders", lazy="selectin")
    receiver_id: Mapped[int] = mapped_column(ForeignKey("ckl.receivers.id"), comment="Получатель", nullable=False)
    receiver: Mapped["Receivers"] = relationship("Receivers", lazy="selectin")


class CargoItems(BaseModel):
    # __tablename__ = "cargo_items"
    __table_args__ = dict(schema=db_schema, comment="Товары в грузах")

    cargo_id: Mapped[int] = mapped_column(ForeignKey("ckl.cargos.id"), comment="Груз", nullable=False)
    # cargo: Mapped["Cargos"] = relationship("Cargos", lazy="selectin")

    name: Mapped[str] = mapped_column(comment="Наименование товара", nullable=False)
    description: Mapped[str] = mapped_column(comment="Дополнительное описание товара", nullable=True)
    hs_code: Mapped[str] = mapped_column(comment="Код ТН ВЭД", nullable=False)
    quantity: Mapped[float] = mapped_column(comment="Количество", nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(comment="Единица измерения", nullable=False)
    net_weight_kg: Mapped[float] = mapped_column(comment="Вес нетто в кг", nullable=False)
    gross_weight_kg: Mapped[float] = mapped_column(comment="Вес брутто в кг", nullable=False)
    unit_price: Mapped[float] = mapped_column(comment="Цена за единицу", nullable=False)
    total_value: Mapped[float] = mapped_column(comment="Общая стоимость", nullable=False)
    barcode: Mapped[str] = mapped_column(comment="Штрих-код", nullable=True)
    currency: Mapped[str] = mapped_column(comment="Валюта", nullable=False)
    customs_value: Mapped[float] = mapped_column(comment="Таможенная стоимость", nullable=False)
    country_of_origin: Mapped[str] = mapped_column(comment="Страна происхождения", nullable=False)
    origin_country: Mapped[str] = mapped_column(comment="Страна происхождения", nullable=False)
    destination_country: Mapped[str] = mapped_column(comment="Страна назначения", nullable=False)
    is_hazardous: Mapped[bool] = mapped_column(comment="Опасный груз", nullable=False)


class VehicleRouteTrackings(BaseModel):
    # __tablename__ = "vehicle_route_trackings"
    __table_args__ = dict(schema=db_schema, comment="Пересечения отметок")

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicles.id"),
        comment="Транспортное средство",
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(comment="Время фиксации положения", nullable=True)
    shape: Mapped[WKBElement] = mapped_point_column()
    speed_kmh: Mapped[float] = mapped_column(comment="Скорость ТС в км/ч", nullable=True)
    direction_deg: Mapped[int] = mapped_column(comment="Направление движения", nullable=True)
    source: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey("ckl.cameras.id"), comment="Камера", nullable=True)
    weighting_station_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.weighting_stations.id"),
        comment="Весовая станция",
        nullable=True,
    )
    is_stopped: Mapped[bool] = mapped_column(comment="Признак остановки", nullable=False)


class VehicleCustomsCrossings(BaseModel):
    # __tablename__ = "vehicle_customs_crossings"
    __table_args__ = dict(schema=db_schema, comment="Пересечения границы")

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.vehicles.id"),
        comment="Транспортное средство",
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(comment="Направление", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(comment="Время фиксации пересечения границы", nullable=True)
    customs_declaration_id_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_declarations.id"),
        comment="Накладная",
        nullable=False,
    )
    camera_id: Mapped[int] = mapped_column(ForeignKey("ckl.cameras.id"), comment="Камера", nullable=True)
    is_inspection_required: Mapped[bool] = mapped_column(comment="Требуется ли проверка", nullable=False)
    is_inspection_performed: Mapped[bool] = mapped_column(comment="Проверка выполнена", nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("ckl.declaration_statuses.id"), comment="Статус", nullable=False)
    status: Mapped["DeclarationStatuses"] = relationship("DeclarationStatuses", lazy="selectin")
    entry_timestamp: Mapped[datetime] = mapped_column(comment="Время пересечения границы при въезде", nullable=False)
    exit_timestamp: Mapped[datetime] = mapped_column(comment="Время пересечения при выезде", nullable=True)
    inspection_result: Mapped[str] = mapped_column(comment="Результат досмотра", nullable=True)
    remarks: Mapped[str] = mapped_column(Text, comment="Комментарии по грузу", nullable=True)


class Warehouses(BaseModel):
    # __tablename__ = "warehouses"
    __table_args__ = dict(schema=db_schema, comment="Склады")

    name: Mapped[str] = mapped_column(comment="Наименование", nullable=False)
    type: Mapped[str] = mapped_column(comment="Тип склада", nullable=False)
    location_coords: Mapped[WKBElement] = mapped_point_column()
    location_text: Mapped[str] = mapped_column(comment="Адрес или описание расположения", nullable=False)
    region: Mapped[str] = mapped_column(comment="Регион или административная зона", nullable=False)
    capacity_m3: Mapped[float] = mapped_column(comment="Вместимость в м3", nullable=False)
    contact_person: Mapped[str] = mapped_column(comment="Ответственное лицо или оператор", nullable=False)
    phone: Mapped[str] = mapped_column(comment="Телефон", nullable=False)
    is_active: Mapped[bool] = mapped_column(comment="Активен", nullable=False, default=True)


class DeclarationTypes(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Типы деклараций")
    name: Mapped[str] = mapped_column(comment="Наименование типа декларации", nullable=False)


class DeclarationStatuses(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Статусы деклараций")
    name: Mapped[str] = mapped_column(comment="Наименование статуса", nullable=False)


class PackagingTypes(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Типы упаковки")
    name: Mapped[str] = mapped_column(comment="Наименование типа груза", nullable=False)


class ParticipantRoles(BaseModel):
    __table_args__ = dict(schema=db_schema, comment="Роли участников")
    name: Mapped[str] = mapped_column(comment="Наименование роли", nullable=False)
