from typing import Optional
from datetime import date
from app.modules.common.dto import BaseDto, BasestDto
from app.modules.ckf.dtos import OrganizationDto


class DicOrderStatusDto(BasestDto):
    id: int
    code: Optional[str]
    name: Optional[str]
    description: Optional[str]


class DicOrderTypeDto(BasestDto):
    id: int
    code: Optional[str]
    name: Optional[str]


class DicRiskDegreeDto(BasestDto):
    id: int
    code: Optional[str]
    name: Optional[str]


class DicRiskNameDto(BasestDto):
    id: int
    code: Optional[str]
    name: Optional[str]


class DicRiskTypeDto(BasestDto):
    id: int
    code: Optional[str]
    name: Optional[str]


class RisksDto(BaseDto):
    risk_type: Optional[int]
    risk_name: Optional[int]
    risk_date: Optional[date]
    risk_degree: Optional[int]
    risk_value: Optional[float]
    risk_details: Optional[str]
    order_id: Optional[int]
    exec_id: Optional[int]
    is_ordered: Optional[bool]
    organization_id: Optional[int]
    period: Optional[str]

    # Relationships
    organization: Optional[OrganizationDto] = None
    risk_type_ref: Optional[DicRiskTypeDto] = None
    risk_name_ref: Optional[DicRiskNameDto] = None
    risk_degree_ref: Optional[DicRiskDegreeDto] = None


class RisksFilterDto(BasestDto):
    risk_degree_id: Optional[int] = None
    risk_type_id: Optional[int] = None
    risk_name_id: Optional[int] = None
    iin_bin: Optional[str] = None
