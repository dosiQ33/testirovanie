from datetime import date, datetime
from typing import Any, List, Optional


from app.modules.common.dto import (
    BasestDto,
    BaseDto,
    DtoWithShape
)

class LandsDto(DtoWithShape):
    kad_number: Optional[str]
    change_date: Optional[datetime]
    stop_date: Optional[datetime]
    stop_reason_ru: Optional[str]
    stop_reason_kk: Optional[str]
    square: Optional[float]
    purpose_ru: Optional[str]
    purpose_kk: Optional[str]
    address_code: Optional[str]
    adress_name_ru: Optional[str]
    address_name_kk: Optional[str]

    divisibility_id: int
    functional_id: int
    land_category_id: int
    part_type_id: Optional[int]
    purpose_use_id: int

    start_date: Optional[datetime]
    uniq_identif_economic_charachter: Optional[str]
    ball_boniteta: Optional[str]
    data_reg_boniteta: Optional[str]
    uniq_identif_soil: Optional[str]
    uniq_identif_istorii_izm: Optional[str]
    uniq_identif_pravootnow: Optional[str]
    uniq_identif_docs: Optional[str]
    uniq_identif_zapis_zareg_pravah: Optional[str]
    uniq_identif_restrict: Optional[str]
    status: Optional[int]
    law_status: Optional[str]
    right_status: Optional[str]
    restrict_status: Optional[str]
    economic_status: Optional[str]

    object_id: Optional[str]

    close: Optional[bool]
    stop_reason: Optional[str]
    part_number: Optional[str]

class LandsLegalInfoDto(BasestDto):
    iin: Optional[str] = None
    bin: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    document_name_ru: Optional[str] = None
    start_date: Optional[datetime] = None

class InfrastructureInfoDto(BasestDto):
    electricity: Optional[bool] = None
    water: Optional[bool] = None
    gas: Optional[bool] = None
    sewage: Optional[bool] = None
    internet: Optional[bool] = None
    road_type: Optional[str] = None
    distance_to_city_km: Optional[int] = None

class EcologyInfoDto(BasestDto):
    land_type: str
    restriction: str

class EcologyInfoListDto(BasestDto):
    ecology: List[EcologyInfoDto]

class RestrictionsInfoDto(BasestDto):
    charge_type: Optional[str] = None
    charge_start_date: Optional[datetime] = None
    charge_duration: Optional[str] = None
    arrests: Optional[str] = None
    arrest_start_date: Optional[datetime] = None
    arrest_duration: Optional[str] = None
    other_restrictions: Optional[str] = None
    other_start_date: Optional[date] = None
    other_duration: Optional[str] = None
    subject_id: Optional[int] = None