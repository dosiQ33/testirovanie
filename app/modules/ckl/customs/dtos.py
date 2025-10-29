from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.modules.common.dto import BaseDto, DtoWithShape, BasestDto
from app.modules.common.utils import SerializedGeojson


# Simple lookup table DTOs
class BookingStatusesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class ControlMeasuresDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class CustomsOfficeStatusesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class CustomsOfficeTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class DeclarationStatusesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class DeclarationTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class InspectionResultsDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class InspectionTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class SealStatusesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class SealTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class TransitTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


class WarehouseTypesDto(BaseDto):
    name_kk: Optional[str] = None
    name_ru: Optional[str] = None


# Code-based lookup table DTOs
class CustomsDocumentTypesDto(BaseDto):
    code: Optional[str] = None
    name_ru: Optional[str] = None
    name_kk: Optional[str] = None


class CustomsProceduresDto(BaseDto):
    code: Optional[str] = None
    name_ru: Optional[str] = None
    name_kk: Optional[str] = None


# Junction table DTOs
class CargoCustomsDocumentsDto(BaseDto):
    customs_document_id: Optional[int] = None
    cargo_id: Optional[int] = None


# Complex entity DTOs
class CustomsBookingsDto(BaseDto):
    vehicle_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    customs_office_id: Optional[int] = None
    booking_date: Optional[date] = None
    preferred_entry_timestamp: Optional[datetime] = None
    is_entry: Optional[bool] = None
    status_id: Optional[int] = None
    comments: str
    is_inspection_required: Optional[bool] = None
    inspection_id: Optional[int] = None
    document_number: Optional[str] = None


class CustomsCrossingsDto(BaseDto):
    customs_offices_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    is_entry: Optional[bool] = None
    timestamp: Optional[datetime] = None
    customs_documents_id: Optional[int] = None
    camera_id: Optional[int] = None
    is_inspection_required: Optional[bool] = None
    is_inspected: Optional[bool] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: datetime
    inspection_id: Optional[int] = None
    comments: str


class CustomsDocumentsDto(BaseDto):
    vehicle_id: Optional[int] = None
    declaration_number: Optional[str] = None
    declaration_date: Optional[date] = None
    is_inspected: Optional[bool] = None
    status_id: Optional[int] = None
    comments: str
    type_id: Optional[int] = None
    accompanying_docs: str
    customs_office_id: int
    customs_procedure_id: int
    exporter_code: str
    importer_code: str
    production_country_id: int
    departure_country_id: int
    destination_country_id: int
    total_declaration_sum: Decimal
    total_customs_sum: Decimal
    duty_sum: Decimal
    vat_sum: Decimal
    excise_sum: Decimal
    declaration_type_id: Optional[int] = None
    duty_rate: Decimal
    vat_rate: Decimal
    inspection_id: int
    departure_customs_office_id: int
    destination_customs_office_id: int
    transit_type_id: int
    transportation_route_description: str
    expected_transit_duration: str
    declarant_name: str
    declarant_iin_bin: str
    declarant_address: str
    number_of_packages: int
    package_type_id: int
    customs_seal_id: int
    security_measures: str
    entry_timestamp: datetime
    exit_timestamp: datetime


class CustomsOfficesDto(DtoWithShape):
    code: Optional[str] = None
    name_ru: Optional[str] = None
    name_kk: Optional[str] = None
    kato_code: Optional[str]
    type_id: Optional[int] = None
    address: Optional[str] = None
    rca_code: Optional[str] 
    is_border_point: Optional[bool] = None
    status_id: int
    shape: SerializedGeojson


class CustomsSealsDto(BaseDto):
    number: Optional[str] = None
    type_id: Optional[int] = None
    status_id: Optional[int] = None
    installation_timestamp: Optional[datetime] = None
    removal_timestamp: Optional[datetime] = None
    customs_officer: str
    customs_office_id: Optional[int] = None
    vehicle_id: Optional[int] = None


class InspectionsDto(BaseDto):
    type_id: Optional[int] = None
    control_measure_id: Optional[int] = None
    result_id: Optional[int] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    inspector: str


class SendersRecipientsDto(BaseDto):
    is_foreign: Optional[bool] = None
    name: Optional[str] = None
    iin_bin: str
    organizations_id: int
    country_id: Optional[int] = None
    address: str
    rca_code: str
    phone: str
    email: str
    contact_person: Optional[str] = None
    is_active: Optional[bool] = None

class CustomsCarriersDto(BasestDto):

    id: int
    country_id: int
    doc_number: str
    date_start: date
    address: str
    organization_id: int
    contact_information: str
    iin_bin: str
    document_number: str
    document_date_end: date
    customs_offices_id: int
    other_information: str


class RepresentOfficesDto(BasestDto):

    id: int
    country_id: int
    doc_number: str
    doc_date: date
    organization_id: int
    iin_bin: str