from datetime import date, datetime
from typing import Optional

from app.modules.common.dto import BasestDto, DtoWithShape

class RoadsDto(DtoWithShape):
    code: str
    name: str
    parent_id: Optional[int]
    kato_code: Optional[str]
    type_id: int
    created_at: datetime
    updated_at: Optional[datetime]

class RoadServicesDto(DtoWithShape):
    segment_index: str
    toll_section: bool
    road_id: int
    km_mark: str
    placement_side: str
    reverse_km_mark: str
    service_name: str
    owner_name: str
    owner_contact: str
    ods_category: str
    standard_compliance: bool
    commissioning_year: int
    land_allocation: bool
    engineering_networks: bool
    exits: bool
    fuel_station: bool
    motel: bool
    toilet: bool
    food_point: bool
    retail_point: bool
    showers: bool
    service_station: bool
    car_wash: bool
    medical_point: bool
    parking: bool
    guarded_parking: bool
    entertainment_zone: bool
    picnic_area: bool
    accessible_facilities: bool
    video_surveillance: bool
    region: str
