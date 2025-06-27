from .models import (
    Countries,
    CustomsOffices,
    CustomsProcedures,
    CustomsPoints,
    TransportCompanies,
    VehicleTypes,
    VehicleMakeTypes,
    Vehicles,
    BookingStatuses,
    Bookings,
    CameraTypes,
    Cameras,
    CameraEvents,
    WeightingStations,
    WeightingEvents,
    Senders,
    Receivers,
    CustomsDeclarations,
    Inspections,
    CargoTypes,
    PackageTypes,
    Cargos,
    CargoItems,
    VehicleRouteTrackings,
    VehicleCustomsCrossings,
    Warehouses,
    DeclarationTypes,
    DeclarationStatuses,
    PackagingTypes,
    ParticipantRoles,
)
from datetime import date, datetime
from typing import Optional
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter


class CountriesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

    class Constants(Filter.Constants):
        model = Countries
        search_model_fields = ["name"]


class CustomsOfficesFilter(Filter):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = CustomsOffices
        search_model_fields = ["name"]


class CustomsProceduresFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = CustomsProcedures
        search_model_fields = ["name"]


class CustomsPointsFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    country_border: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    # location_coords: Optional[WKBElement] = None  # Geometry fields are not filterable by default

    class Constants(Filter.Constants):
        model = CustomsPoints
        search_model_fields = ["name"]


class TransportCompaniesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    bin: Optional[str] = None
    is_international: Optional[bool] = None
    vat_number: Optional[str] = None
    country_code: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = TransportCompanies
        search_model_fields = ["name"]


class VehicleTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = VehicleTypes
        search_model_fields = ["name"]


class VehicleMakeTypesFilter(Filter):
    id: Optional[int] = None
    code: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = VehicleMakeTypes
        search_model_fields = ["name"]


class VehiclesFilter(Filter):
    id: Optional[int] = None
    number: Optional[str] = None
    trailer_number: Optional[str] = None
    type_id: Optional[int] = None
    type: Optional[VehicleTypesFilter] = FilterDepends(with_prefix("type", VehicleTypesFilter))
    make_id: Optional[int] = None
    make: Optional[VehicleMakeTypesFilter] = FilterDepends(with_prefix("make", VehicleMakeTypesFilter))
    year: Optional[int] = None
    vin_number: Optional[str] = None
    transport_company_id: Optional[int] = None
    transport_company: Optional[TransportCompaniesFilter] = FilterDepends(
        with_prefix("transport_company", TransportCompaniesFilter)
    )
    country_id: Optional[int] = None
    registration_date: Optional[date] = None
    is_active: Optional[bool] = None
    location_text: Optional[str] = None
    location_timestamp: Optional[datetime] = None

    class Constants(Filter.Constants):
        model = Vehicles
        search_model_fields = ["number"]


class BookingStatusesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = BookingStatuses
        search_model_fields = ["name"]


class BookingsFilter(Filter):
    id: Optional[int] = None
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    customs_point_id: Optional[int] = None
    customs_point: Optional[CustomsPointsFilter] = FilterDepends(with_prefix("customs_point", CustomsPointsFilter))
    booking_date: Optional[date] = None
    entry_datetime: Optional[datetime] = None
    is_exit: Optional[bool] = None
    booking_status_id: Optional[int] = None
    booking_status: Optional[BookingStatusesFilter] = FilterDepends(with_prefix("booking_status", BookingStatusesFilter))
    is_inspection_required: Optional[bool] = None
    document_number: Optional[str] = None
    comments: Optional[str] = None

    class Constants(Filter.Constants):
        model = Bookings


class CameraTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = CameraTypes
        search_model_fields = ["name"]


class CamerasFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    type_id: Optional[int] = None
    type: Optional[CameraTypesFilter] = FilterDepends(with_prefix("type", CameraTypesFilter))
    location_text: Optional[str] = None
    direction_supported: Optional[str] = None
    operator_name: Optional[str] = None
    installation_date: Optional[date] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Cameras
        search_model_fields = ["name"]


class CameraEventsFilter(Filter):
    id: Optional[int] = None
    camera_id: Optional[int] = None
    camera: Optional[CamerasFilter] = FilterDepends(with_prefix("camera", CamerasFilter))
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    speed: Optional[float] = None
    direction: Optional[str] = None
    image_url: Optional[str] = None
    is_recognized: Optional[bool] = None
    remarks: Optional[str] = None

    class Constants(Filter.Constants):
        model = CameraEvents


class WeightingStationsFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    location_text: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = None
    has_camera: Optional[bool] = None
    operator_name: Optional[str] = None
    installation_date: Optional[date] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = WeightingStations
        search_model_fields = ["name"]


class WeightingEventsFilter(Filter):
    id: Optional[int] = None
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    weighting_station_id: Optional[int] = None
    weighting_station: Optional[WeightingStationsFilter] = FilterDepends(
        with_prefix("weighting_station", WeightingStationsFilter)
    )
    timestamp: Optional[datetime] = None
    gross_weight_kg: Optional[float] = None
    tare_weight_kg: Optional[float] = None
    net_weight_kg: Optional[float] = None
    allowed_weight_kg: Optional[float] = None
    is_overload: Optional[bool] = None
    overload_kg: Optional[float] = None
    operator_name: Optional[str] = None
    camera_id: Optional[int] = None
    camera: Optional[CamerasFilter] = FilterDepends(with_prefix("camera", CamerasFilter))
    image_url: Optional[str] = None
    remarks: Optional[str] = None

    class Constants(Filter.Constants):
        model = WeightingEvents


class SendersFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    iin_bin: Optional[str] = None
    is_foreign: Optional[bool] = None
    country_id: Optional[int] = None
    country: Optional[CountriesFilter] = FilterDepends(with_prefix("country", CountriesFilter))
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Senders
        search_model_fields = ["name"]


class ReceiversFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    iin_bin: Optional[str] = None
    is_foreign: Optional[bool] = None
    country_id: Optional[int] = None
    country: Optional[CountriesFilter] = FilterDepends(with_prefix("country", CountriesFilter))
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Receivers
        search_model_fields = ["name"]


class DeclarationTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DeclarationTypes
        search_model_fields = ["name"]


class CustomsDeclarationsFilter(Filter):
    id: Optional[int] = None
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    number: Optional[str] = None
    accompanying_docs: Optional[str] = None
    customs_office_id: Optional[int] = None
    customs_office: Optional[CustomsOfficesFilter] = FilterDepends(with_prefix("customs_office", CustomsOfficesFilter))
    declaration_date: Optional[date] = None
    status_id: Optional[int] = None
    customs_procedure_id: Optional[int] = None
    customs_procedure: Optional[CustomsProceduresFilter] = FilterDepends(
        with_prefix("customs_procedure", CustomsProceduresFilter)
    )
    exporter_bin: Optional[str] = None
    importer_bin: Optional[str] = None
    origin_country_id: Optional[int] = None
    origin_country: Optional[CountriesFilter] = FilterDepends(with_prefix("origin_country", CountriesFilter))
    registration_country_id: Optional[int] = None
    registration_country: Optional[CountriesFilter] = FilterDepends(with_prefix("registration_country", CountriesFilter))
    departure_country_id: Optional[int] = None
    departure_country: Optional[CountriesFilter] = FilterDepends(with_prefix("departure_country", CountriesFilter))
    destination_country_id: Optional[int] = None
    destination_country: Optional[CountriesFilter] = FilterDepends(with_prefix("destination_country", CountriesFilter))
    border_crossing_point_id: Optional[int] = None
    release_date: Optional[datetime] = None
    total_invoice_amount: Optional[float] = None
    contract_currency: Optional[str] = None
    total_customs_value: Optional[float] = None
    duty_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    excise_amount: Optional[float] = None
    declaration_type_id: Optional[int] = None
    declaration_type: Optional[DeclarationTypesFilter] = FilterDepends(with_prefix("declaration_type", DeclarationTypesFilter))
    item_id: Optional[int] = None
    invoice_value: Optional[float] = None
    customs_value: Optional[float] = None
    duty_rate: Optional[float] = None
    vat_rate: Optional[float] = None
    participant_id: Optional[int] = None
    role_id: Optional[int] = None
    participant_bin: Optional[str] = None
    participant_name: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Constants(Filter.Constants):
        model = CustomsDeclarations


class InspectionsFilter(Filter):
    id: Optional[int] = None
    type: Optional[str] = None
    timestamp: Optional[datetime] = None
    inspector: Optional[str] = None
    result: Optional[str] = None

    class Constants(Filter.Constants):
        model = Inspections


class CargoTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = CargoTypes
        search_model_fields = ["name"]


class PackageTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = PackageTypes
        search_model_fields = ["name"]


class CargosFilter(Filter):
    id: Optional[int] = None
    customs_declaration_id: Optional[int] = None
    customs_declaration: Optional[CustomsDeclarationsFilter] = FilterDepends(
        with_prefix("customs_declaration", CustomsDeclarationsFilter)
    )
    description: Optional[str] = None
    cargo_type_id: Optional[int] = None
    cargo_type: Optional[CargoTypesFilter] = FilterDepends(with_prefix("cargo_type", CargoTypesFilter))
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    package_type_id: Optional[int] = None
    temperature_mode: Optional[str] = None
    is_dangerous: Optional[bool] = None
    sender_id: Optional[int] = None
    sender: Optional[SendersFilter] = FilterDepends(with_prefix("sender", SendersFilter))
    receiver_id: Optional[int] = None
    receiver: Optional[ReceiversFilter] = FilterDepends(with_prefix("receiver", ReceiversFilter))

    class Constants(Filter.Constants):
        model = Cargos


class CargoItemsFilter(Filter):
    id: Optional[int] = None
    cargo_id: Optional[int] = None
    cargo: Optional[CargosFilter] = FilterDepends(with_prefix("cargo", CargosFilter))
    name: Optional[str] = None
    description: Optional[str] = None
    hs_code: Optional[str] = None
    quantity: Optional[float] = None
    unit_of_measure: Optional[str] = None
    net_weight_kg: Optional[float] = None
    gross_weight_kg: Optional[float] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    barcode: Optional[str] = None
    currency: Optional[str] = None
    customs_value: Optional[float] = None
    country_of_origin: Optional[str] = None
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    is_hazardous: Optional[bool] = None

    class Constants(Filter.Constants):
        model = CargoItems


class VehicleRouteTrackingsFilter(Filter):
    id: Optional[int] = None
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    timestamp: Optional[datetime] = None
    speed_kmh: Optional[float] = None
    direction_deg: Optional[int] = None
    source: Optional[str] = None
    camera_id: Optional[int] = None
    camera: Optional[CamerasFilter] = FilterDepends(with_prefix("camera", CamerasFilter))
    weighting_station_id: Optional[int] = None
    weighting_station: Optional[WeightingStationsFilter] = FilterDepends(
        with_prefix("weighting_station", WeightingStationsFilter)
    )
    is_stopped: Optional[bool] = None

    class Constants(Filter.Constants):
        model = VehicleRouteTrackings


class VehicleCustomsCrossingsFilter(Filter):
    id: Optional[int] = None
    vehicle_id: Optional[int] = None
    vehicle: Optional[VehiclesFilter] = FilterDepends(with_prefix("vehicle", VehiclesFilter))
    direction: Optional[str] = None
    timestamp: Optional[datetime] = None
    customs_declaration_id_id: Optional[int] = None
    customs_declaration: Optional[CustomsDeclarationsFilter] = FilterDepends(
        with_prefix("customs_declaration", CustomsDeclarationsFilter)
    )
    camera_id: Optional[int] = None
    camera: Optional[CamerasFilter] = FilterDepends(with_prefix("camera", CamerasFilter))
    is_inspection_required: Optional[bool] = None
    is_inspection_performed: Optional[bool] = None
    status_id: Optional[int] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    inspection_result: Optional[str] = None
    remarks: Optional[str] = None

    class Constants(Filter.Constants):
        model = VehicleCustomsCrossings


class WarehousesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    location_text: Optional[str] = None
    region: Optional[str] = None
    capacity_m3: Optional[float] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Warehouses
        search_model_fields = ["name"]


class DeclarationStatusesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DeclarationStatuses
        search_model_fields = ["name"]


class PackagingTypesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = PackagingTypes
        search_model_fields = ["name"]


class ParticipantRolesFilter(Filter):
    id: Optional[int] = None

    class Constants(Filter.Constants):
        model = ParticipantRoles
