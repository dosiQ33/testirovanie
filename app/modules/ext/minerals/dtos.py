from typing import Optional

from pydantic import Field
from typing import List
from app.modules.common.dto import BasestDto, DtoWithShape
from app.modules.common.utils import SerializedGeojson

from datetime import date


class MineralsLocContractsDto(BasestDto):
    id: int
    bin: Optional[str]
    name: Optional[str]
    locnumber: Optional[str]
    field_5: Optional[str]

    geom: SerializedGeojson


class MineralsLocContractsFilterDto(BasestDto):
    territory: Optional[str] = Field(
        None,
        description="Получить записи пересекающиеся с данной геометрией. Координаты в формате WKT SRID=4326",
        example="POLYGON((70.0 50.0, 70.0 60.0, 80.0 60.0, 80.0 50.0, 70.0 50.0))",
    )

class IucMineralsDto(DtoWithShape):
    id: int
    loc_number: Optional[str] = None
    loc_date: Optional[date] = None 
    loc_type_id: int
    organization_id: int
    official_org_xin: Optional[str] = None
    official_org_name: Optional[str] = None
    loc_status: Optional[str] = None
    created_at: Optional[date] = None  

class IucMineralsResponseDto(BasestDto):
    loc_date: date
    official_org_xin: int
    official_org_name: str
    loc_status: str
    name_ru: str
    iin_bin: int
    address: str

class IucMineralsContractsResponseDto(BasestDto):
    id: int
    loc_number: str
    name_ru: str
    loc_type: str

class IucMineralsContractsResponseListDto(BasestDto):
    contracts: List[IucMineralsContractsResponseDto]

class IucMineralsFilterRequestDto(BasestDto):
    id: List[int]