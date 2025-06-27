"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from datetime import date, datetime
from typing import Optional

from app.modules.common.dto import BasestDto
from app.modules.common.utils import SerializedGeojson


class CountriesDto(BasestDto):
    id: int
    name: str
    code: str


class DeclarationTypesDto(BasestDto):
    id: int
    name: str


class DeclarationStatusesDto(BasestDto):
    id: int
    name: str


class CustomsPointsDto(BasestDto):
    id: int
    name: str
    country_border: str
    location_name: str
    location_address: str
    location_coords: SerializedGeojson


class TransportCompaniesDto(BasestDto):
    id: int
    name: str
    bin: Optional[str]
    is_international: bool
    vat_number: Optional[str]
    country_code: str
    registration_number: str
    address: str
    phone: str
    email: Optional[str]
    contact_person: Optional[str]
    is_active: bool


class VehicleTypesDto(BasestDto):
    id: int
    name: str


class VehiclesDto(BasestDto):
    id: int
    number: str
    trailer_number: Optional[str]
    type_id: int
    type: Optional[VehicleTypesDto]
    make: str
    location_gps: SerializedGeojson
    location_text: Optional[str]
    location_timestamp: Optional[datetime]
    year: Optional[int]
    vin_number: str
    transport_company_id: int
    transport_company: Optional[TransportCompaniesDto]
    country_registration: str
    registration_date: date
    is_active: bool


class VehicleRouteTrackingsDto(BasestDto):
    id: int
    vehicle_id: int
    timestamp: Optional[datetime]
    shape: SerializedGeojson
    speed_kmh: Optional[float]
    direction_deg: Optional[int]
    source: str
    camera_id: Optional[int]
    weighting_station_id: Optional[int]
    is_stopped: bool


class VehicleCustomsCrossingsDto(BasestDto):
    id: int
    vehicle_id: int
    direction: str
    timestamp: Optional[datetime]
    customs_declaration_id_id: int
    camera_id: Optional[int]
    is_inspection_required: bool
    is_inspection_performed: bool
    status_id: int
    entry_timestamp: datetime
    exit_timestamp: Optional[datetime]
    inspection_result: Optional[str]
    remarks: Optional[str]


class CameraTypesDto(BasestDto):
    id: int
    name: str


class CamerasDto(BasestDto):
    id: int
    name: str
    type_id: int
    type: Optional[CameraTypesDto]
    shape: SerializedGeojson
    location_text: str
    direction_supported: str
    operator_name: str
    installation_date: date
    is_active: bool


class CameraEventsDto(BasestDto):
    id: int
    camera_id: int
    vehicle_id: int
    speed: float
    direction: str
    image_url: str
    is_recognized: bool
    remarks: Optional[str]


class WeightingStationsDto(BasestDto):
    id: int
    name: str
    location_coords: SerializedGeojson
    location_text: str
    region: str
    type: str
    has_camera: bool
    operator_name: str
    installation_date: date
    is_active: bool


class WeightingEventsDto(BasestDto):
    id: int
    vehicle_id: int
    weighting_station_id: int
    timestamp: datetime
    gross_weight_kg: float
    tare_weight_kg: float
    net_weight_kg: float
    allowed_weight_kg: float
    is_overload: bool
    overload_kg: float
    operator_name: str
    camera_id: Optional[int]
    image_url: Optional[str]
    remarks: Optional[str]


class SendersDto(BasestDto):
    id: int
    name: str
    iin_bin: Optional[str]
    is_foreign: bool
    country_id: int
    country: Optional[CountriesDto]
    address: str
    phone: str
    email: Optional[str]
    contact_person: Optional[str]
    is_active: bool


class ReceiversDto(BasestDto):
    id: int
    name: str
    iin_bin: Optional[str]
    is_foreign: bool
    country_id: int
    country: Optional[CountriesDto]
    address: str
    phone: str
    email: Optional[str]
    contact_person: Optional[str]
    is_active: bool


class CargosDto(BasestDto):
    id: int
    customs_declaration_id: int
    description: str
    cargo_type_id: int
    weight_kg: float
    volume_m3: float
    package_type_id: int
    temperature_mode: Optional[str]
    is_dangerous: bool
    sender_id: int
    receiver_id: int


class CargoItemsDto(BasestDto):
    id: int
    cargo_id: int
    name: str
    description: Optional[str]
    hs_code: str
    quantity: float
    unit_of_measure: str
    net_weight_kg: float
    gross_weight_kg: float
    unit_price: float
    total_value: float
    barcode: Optional[str]
    currency: str
    customs_value: float
    country_of_origin: str
    origin_country: str
    destination_country: str
    is_hazardous: bool


class CustomsOfficesDto(BasestDto):
    id: int
    code: str
    name: str


class CustomsProceduresDto(BasestDto):
    id: int
    name: str


class CustomsDeclarationsDto(BasestDto):
    id: int
    vehicle_id: Optional[int]
    vehicle: Optional[VehiclesDto]
    number: Optional[str]
    accompanying_docs: Optional[str]
    customs_office_id: Optional[int]
    customs_office: Optional[CustomsOfficesDto]
    declaration_date: Optional[date]
    status_id: Optional[int]
    customs_procedure_id: Optional[int]
    customs_procedure: Optional[CustomsProceduresDto]
    exporter_bin: Optional[str]
    importer_bin: Optional[str]
    origin_country_id: Optional[int]
    origin_country: Optional[CountriesDto]
    registration_country_id: Optional[int]
    registration_country: Optional[CountriesDto]
    departure_country_id: Optional[int]
    departure_country: Optional[CountriesDto]
    destination_country_id: Optional[int]
    destination_country: Optional[CountriesDto]
    border_crossing_point_id: Optional[int]
    release_date: Optional[datetime]
    total_invoice_amount: Optional[float]
    contract_currency: Optional[str]
    total_customs_value: Optional[float]
    duty_amount: Optional[float]
    vat_amount: Optional[float]
    excise_amount: Optional[float]
    declaration_type_id: Optional[int]
    declaration_type: Optional[DeclarationTypesDto]
    item_id: Optional[int]
    invoice_value: Optional[float]
    customs_value: Optional[float]
    duty_rate: Optional[float]
    vat_rate: Optional[float]
    participant_id: Optional[int]
    role_id: Optional[int]
    participant_bin: Optional[str]
    participant_name: Optional[str]
    address: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class VehicleMakeTypesDto(BasestDto):
    id: int
    code: int
    name: str


class BookingStatusesDto(BasestDto):
    id: int
    name: str


class BookingsDto(BasestDto):
    id: int
    vehicle_id: Optional[int]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    customs_point_id: Optional[int]
    booking_date: Optional[date]
    entry_datetime: Optional[datetime]
    is_exit: bool
    booking_status_id: Optional[int]
    is_inspection_required: Optional[bool]
    document_number: Optional[str]
    comments: str


class PackagingTypesDto(BasestDto):
    id: int
    name: str


class ParticipantRolesDto(BasestDto):
    id: int
    name: str


class InspectionsDto(BasestDto):
    id: int
    type: str
    timestamp: datetime
    inspector: str
    result: str


class CargoTypesDto(BasestDto):
    id: int
    name: str


class PackageTypesDto(BasestDto):
    id: int
    name: str


class WarehousesDto(BasestDto):
    id: int
    name: str
    type: str
    location_coords: SerializedGeojson
    location_text: str
    region: str
    capacity_m3: float
    contact_person: str
    phone: str
    is_active: bool
