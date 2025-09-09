from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from decimal import Decimal
from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BaseModel

db_schema = "ckl"


def mapped_point_column() -> Mapped[WKBElement]:
    return mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Координаты",
        nullable=True,
    )


class BookingStatuses(BaseModel):
    __tablename__ = "booking_statuses"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class CargoCustomsDocuments(BaseModel):
    __tablename__ = "cargo_customs_documents"
    __table_args__ = dict(schema=db_schema)

    customs_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_documents.id"), comment="Документ", nullable=True
    )
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.cargos.id"), comment="Груз", nullable=True)


class ControlMeasures(BaseModel):
    __tablename__ = "control_measures"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class CustomsBookings(BaseModel):
    __tablename__ = "customs_bookings"
    __table_args__ = dict(schema=db_schema)

    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.vehicles.id"), comment="Транспортное средство", nullable=True)
    driver_name: Mapped[str | None] = mapped_column(name="driver_name", comment="ФИО водителя", nullable=True)
    driver_phone: Mapped[str | None] = mapped_column(name="driver_phone", comment="Контактный номер водителя", nullable=True)
    customs_office_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Таможенный орган", nullable=True
    )
    booking_date: Mapped[date | None] = mapped_column(name="booking_date", comment="Дата бронирования", nullable=True)
    preferred_entry_timestamp: Mapped[datetime | None] = mapped_column(
        name="preferred_entry_timestamp", comment="Желаемое время прибытия", nullable=True
    )
    is_entry: Mapped[bool | None] = mapped_column(name="is_entry", comment="Въезд", nullable=True)
    status_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.booking_statuses.id"), comment="Статус бронирования", nullable=True
    )
    comments: Mapped[str] = mapped_column(Text, comment="Дополнительная информация или примечание", nullable=False)
    is_inspection_required: Mapped[bool | None] = mapped_column(
        name="is_inspection_required", comment="Требуется ли досмотр", nullable=True
    )
    inspection_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.inspections.id"), comment="Уникальный ID досмотра", nullable=True
    )
    document_number: Mapped[str | None] = mapped_column(
        name="document_number", comment="Номер сопроводительного документа (ГТД, CMR и т.п.)", nullable=True
    )


class CustomsCrossings(BaseModel):
    __tablename__ = "customs_crossings"
    __table_args__ = dict(schema=db_schema)

    customs_offices_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Уникальный идентификатор таможенного пункта в БД", nullable=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.vehicles.id"), comment="Транспортное средство", nullable=True)
    is_entry: Mapped[bool | None] = mapped_column(name="is_entry", comment="Въезд", nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(
        name="timestamp", comment="Время фиксации пересечения границы", nullable=True
    )
    customs_documents_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_documents.id"), comment="Таможенные документы", nullable=True
    )
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.cameras.id"), comment="Камера фиксации движения", nullable=True)
    is_inspection_required: Mapped[bool | None] = mapped_column(
        name="is_inspection_required", comment="Необходим досмотр", nullable=True
    )
    is_inspected: Mapped[bool | None] = mapped_column(name="is_inspected", comment="Досмотрено", nullable=True)
    entry_timestamp: Mapped[datetime | None] = mapped_column(
        name="entry_timestamp", comment="Время пересечения границы при въезде", nullable=True
    )
    exit_timestamp: Mapped[datetime] = mapped_column(
        name="exit_timestamp", comment="Время пересечения при выезде", nullable=False
    )
    inspection_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.inspections.id"), comment="Досмотр", nullable=True)
    comments: Mapped[str] = mapped_column(Text, comment="Комментарии по грузу", nullable=False)


class CustomsDocumentTypes(BaseModel):
    __tablename__ = "customs_document_types"
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str | None] = mapped_column(name="code", comment="Код марки ТС", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)
    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)


class CustomsDocuments(BaseModel):
    __tablename__ = "customs_documents"
    __table_args__ = dict(schema=db_schema)

    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.vehicles.id"), comment="Транспортное средство", nullable=True)
    declaration_number: Mapped[str | None] = mapped_column(name="declaration_number", comment="Номер декларации", nullable=True)
    declaration_date: Mapped[date | None] = mapped_column(
        name="declaration_date", comment="Дата регистрации декларации", nullable=True
    )
    is_inspected: Mapped[bool | None] = mapped_column(name="is_inspected", comment="Досмотрено", nullable=True)
    status_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_office_statuses.id"), comment="Статус декларации", nullable=True
    )
    comments: Mapped[str] = mapped_column(Text, comment="Примечания", nullable=False)
    type_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_document_types.id"), comment="Тип документа", nullable=True
    )
    accompanying_docs: Mapped[str] = mapped_column(Text, comment="Список сопровождающих документов", nullable=False)
    customs_office_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Таможенный органа оформления", nullable=False
    )
    customs_procedure_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_procedures.id"), comment="Таможенная процедура", nullable=False
    )
    exporter_code: Mapped[str] = mapped_column(name="exporter_code", comment="Налоговый идентификатор экспортёра", nullable=False)
    importer_code: Mapped[str] = mapped_column(name="importer_code", comment="Налоговый идентификатор импортёра", nullable=False)
    production_country_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.countries.id"), comment="Страна происхождения товара", nullable=False
    )
    departure_country_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.countries.id"), comment="Страна отправления", nullable=False
    )
    destination_country_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.countries.id"), comment="Страна назначения", nullable=False
    )
    total_declaration_sum: Mapped[Decimal] = mapped_column(comment="Общая стоимость по декларации", nullable=False)
    total_customs_sum: Mapped[Decimal] = mapped_column(comment="Таможенная стоимость", nullable=False)
    duty_sum: Mapped[Decimal] = mapped_column(comment="Сумма начисленных пошлин", nullable=False)
    vat_sum: Mapped[Decimal] = mapped_column(comment="Сумма начисленного НДС", nullable=False)
    excise_sum: Mapped[Decimal] = mapped_column(comment="Сумма акциза", nullable=False)
    declaration_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.declaration_types.id"), comment="Тип декларации", nullable=True
    )
    duty_rate: Mapped[Decimal] = mapped_column(comment="Ставка пошлины", nullable=False)
    vat_rate: Mapped[Decimal] = mapped_column(comment="Ставка НДС", nullable=False)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("ckl.inspections.id"), comment="Уникальный ID досмотра", nullable=False)
    departure_customs_office_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Код таможенного органа отправления", nullable=False
    )
    destination_customs_office_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Код таможенного органа назначения", nullable=False
    )
    transit_type_id: Mapped[int] = mapped_column(ForeignKey("ckl.transit_types.id"), comment="Тип транзита", nullable=False)
    transportation_route_description: Mapped[str] = mapped_column(Text, comment="Описание маршрута", nullable=False)
    expected_transit_duration: Mapped[str] = mapped_column(INTERVAL, comment="Ожидаемое время в пути", nullable=False)
    declarant_name: Mapped[str] = mapped_column(name="declarant_name", comment="Наименование или ФИО декларанта", nullable=False)
    declarant_iin_bin: Mapped[str] = mapped_column(name="declarant_iin_bin", comment="БИН или ИИН декларанта", nullable=False)
    declarant_address: Mapped[str] = mapped_column(Text, comment="Адрес декларанта", nullable=False)
    number_of_packages: Mapped[int] = mapped_column(name="number_of_packages", comment="Количество мест", nullable=False)
    package_type_id: Mapped[int] = mapped_column(ForeignKey("ckl.package_types.id"), comment="Тип упаковки", nullable=False)
    customs_seal_id: Mapped[int] = mapped_column(ForeignKey("ckl.customs_seals.id"), comment="Пломбы", nullable=False)
    security_measures: Mapped[str] = mapped_column(Text, comment="Гарантии, депозиты и т.п.", nullable=False)
    entry_timestamp: Mapped[datetime] = mapped_column(
        name="entry_timestamp", comment="Дата/время начала транзита", nullable=False
    )
    exit_timestamp: Mapped[datetime] = mapped_column(
        name="exit_timestamp", comment="Дата/время завершения транзита", nullable=False
    )


class CustomsOfficeStatuses(BaseModel):
    __tablename__ = "customs_office_statuses"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class CustomsOfficeTypes(BaseModel):
    __tablename__ = "customs_office_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class CustomsOffices(BaseModel):
    __tablename__ = "customs_offices"
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str | None] = mapped_column(name="code", comment="Код таможенного органа", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)
    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    kato_code: Mapped[str] = mapped_column(name="kato_code", comment="Регион (область/город)", nullable=False)
    type_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_office_types.id"), comment="Тип таможенного органа", nullable=True
    )
    road_id: Mapped[int] = mapped_column(
        ForeignKey("ckl.roads.id"), comment="Идентификатор дороги", nullable=False
    )
    address: Mapped[str | None] = mapped_column(name="address", comment="Адрес местонахождения", nullable=True)
    rca_code: Mapped[str] = mapped_column(name="rca_code", comment="Код РКА", nullable=False)
    is_border_point: Mapped[bool | None] = mapped_column(name="is_border_point", comment="Приграничный пункт", nullable=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("ckl.customs_office_statuses.id"), comment="Статус", nullable=False)
    shape: Mapped[int] = mapped_point_column()


class CustomsProcedures(BaseModel):
    __tablename__ = "customs_procedures"
    __table_args__ = dict(schema=db_schema)

    code: Mapped[str | None] = mapped_column(name="code", comment="Код марки ТС", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)
    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)


class CustomsSeals(BaseModel):
    __tablename__ = "customs_seals"
    __table_args__ = dict(schema=db_schema)

    number: Mapped[str | None] = mapped_column(
        name="number", comment="Номер пломбы (наносится на физическую пломбу)", nullable=True
    )
    type_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.seal_types.id"), comment="Тип пломбы", nullable=True)
    status_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.seal_statuses.id"), comment="Статус пломбы", nullable=True)
    installation_timestamp: Mapped[datetime | None] = mapped_column(
        name="installation_timestamp", comment="Дата и время установки пломбы", nullable=True
    )
    removal_timestamp: Mapped[datetime | None] = mapped_column(
        name="removal_timestamp", comment="Дата и время снятия", nullable=True
    )
    customs_officer: Mapped[str] = mapped_column(
        name="customs_officer", comment="Сотрудник, установившего пломбу", nullable=False
    )
    customs_office_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.customs_offices.id"), comment="Таможенный орган, где установлена пломба", nullable=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.vehicles.id"), comment="Транспортное средство", nullable=True)


class DeclarationStatuses(BaseModel):
    __tablename__ = "declaration_statuses"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class DeclarationTypes(BaseModel):
    __tablename__ = "declaration_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class InspectionResults(BaseModel):
    __tablename__ = "inspection_results"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class InspectionTypes(BaseModel):
    __tablename__ = "inspection_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class Inspections(BaseModel):
    __tablename__ = "inspections"
    __table_args__ = dict(schema=db_schema)

    type_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.inspection_types.id"), comment="Тип досмотра", nullable=True)
    control_measure_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.control_measures.id"), comment="Меры контроля", nullable=True
    )
    result_id: Mapped[int | None] = mapped_column(
        ForeignKey("ckl.inspection_results.id"), comment="Результат досмотра", nullable=True
    )
    start_timestamp: Mapped[datetime | None] = mapped_column(
        name="start_timestamp", comment="Дата начала контроля", nullable=True
    )
    end_timestamp: Mapped[datetime | None] = mapped_column(
        name="end_timestamp", comment="Дата завершения контроля", nullable=True
    )
    inspector: Mapped[str] = mapped_column(name="inspector", comment="ФИО", nullable=False)


class SealStatuses(BaseModel):
    __tablename__ = "seal_statuses"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class SealTypes(BaseModel):
    __tablename__ = "seal_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class SendersRecipients(BaseModel):
    __tablename__ = "senders_recipients"
    __table_args__ = dict(schema=db_schema)

    is_foreign: Mapped[bool | None] = mapped_column(name="is_foreign", comment="Иностранный", nullable=True)
    name: Mapped[str | None] = mapped_column(name="name", comment="Полное наименование", nullable=True)
    iin_bin: Mapped[str] = mapped_column(name="iin_bin", comment="БИН (для юр. лица) или ИИН (для физ. лица)", nullable=False)
    organizations_id: Mapped[int] = mapped_column(
        ForeignKey("public.organizations.id"), comment="Ссылка на таблицу организаций", nullable=False
    )
    country_id: Mapped[int | None] = mapped_column(ForeignKey("ckl.countries.id"), comment="Страна", nullable=True)
    address: Mapped[str] = mapped_column(name="address", comment="Адрес", nullable=False)
    rca_code: Mapped[str] = mapped_column(name="rca_code", comment="Код РКА", nullable=False)
    phone: Mapped[str] = mapped_column(name="phone", comment="Телефон", nullable=False)
    email: Mapped[str] = mapped_column(name="email", comment="Электронная почта", nullable=False)
    contact_person: Mapped[str | None] = mapped_column(name="contact_person", comment="Контактное лицо", nullable=True)
    is_active: Mapped[bool | None] = mapped_column(name="is_active", comment="Признак активности записи", nullable=True)


class TransitTypes(BaseModel):
    __tablename__ = "transit_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)


class WarehouseTypes(BaseModel):
    __tablename__ = "warehouse_types"
    __table_args__ = dict(schema=db_schema)

    name_kk: Mapped[str | None] = mapped_column(name="name_kk", comment="Наименование на казахском языке", nullable=True)
    name_ru: Mapped[str | None] = mapped_column(name="name_ru", comment="Наименование на русском языке", nullable=True)
