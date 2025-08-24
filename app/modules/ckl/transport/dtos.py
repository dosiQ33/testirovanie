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