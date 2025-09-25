from datetime import date, datetime
from typing import Optional

from app.modules.common.dto import BasestDto, DtoWithShape
from app.modules.common.utils import SerializedGeojson

class VehiclesDto(DtoWithShape):
    number: str
    type_id: int
    make_id: int
    shape: int
    address: Optional[str]
    kato_code: Optional[str]
    rca_code: Optional[str]
    road_id: int
    year: Optional[int]
    vin_number: str
    transport_company_id: int
    country_id: int
    registration_date: date
    is_active: bool
    has_customs_booking: bool

class TransportCompaniesDto(BasestDto):
    id: int
    is_international: bool
    bin: Optional[str] 
    organization_id: Optional[int] 
    name: str 
    vat_number: Optional[str] 
    country_id: int 
    registration_number: str 
    address: str 
    phone: str 
    email: Optional[str] 
    contact_person: Optional[str] 
    is_active: bool
    created_at: datetime
    updated_at: datetime

class VehicleGeoInfoResponse(BasestDto):
    raion: str
    oblast: str
    last_event_timestamp: Optional[datetime]
    road_name: str
    date_of_booking: datetime
    customs_office_name: str

class WarehousesDto(BasestDto):
    id:int
    country_id: int
    type_id: int
    shape: int
    address: str
    date_start: date
    rca_code: str
    capacity: str
    contact_person: str
    is_active: bool
    document_number: str
    contact_information: str
    iin_bin: str
    customs_offices_id: int
    other_information: str
    organisation_id: int
    created_at: datetime
    updated_at: datetime