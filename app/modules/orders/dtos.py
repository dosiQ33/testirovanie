from typing import Optional, List
from datetime import date
from app.modules.common.dto import BaseDto, BasestDto
from app.modules.common.utils import SerializedGeojson


class OrdersOrganizationDto(BaseDto):
    iin_bin: str
    name_ru: str
    name_kk: Optional[str] = None
    date_start: Optional[date] = None
    date_stop: Optional[date] = None
    nds_number: Optional[int] = None
    nds_date_reg: Optional[str] = None
    address: Optional[str] = None
    shape: Optional[SerializedGeojson] = None
    ugd_id: int
    oked_id: Optional[int] = None
    tax_regime_id: Optional[int] = None
    reg_type_id: Optional[int] = None
    leader_id: Optional[int] = None
    knn: Optional[float] = None
    knn_co: Optional[float] = None


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
    risk_type_ref: Optional[DicRiskTypeDto] = None
    risk_name_ref: Optional[DicRiskNameDto] = None
    risk_degree_ref: Optional[DicRiskDegreeDto] = None


class RisksFilterDto(BasestDto):
    risk_degree_id: Optional[int] = None
    risk_type_id: Optional[int] = None
    risk_name_id: Optional[int] = None
    iin_bin: Optional[str] = None


class RiskUpdateDto(BasestDto):
    """DTO для обновления риска"""

    order_id: Optional[int] = None
    is_ordered: Optional[bool] = None


class RiskBulkUpdateDto(BasestDto):
    """DTO для массового обновления рисков"""

    risk_ids: List[int]
    order_id: Optional[int] = None
    is_ordered: Optional[bool] = None


class RiskUpdateResponseDto(BasestDto):
    """DTO для ответа об обновлении"""

    updated_count: int
    message: str


class OrderCreateDto(BasestDto):
    """DTO для создания поручения"""

    order_date: date
    order_deadline: Optional[date] = None
    order_num: Optional[int] = None
    employee_id: Optional[int] = None
    order_status: Optional[int] = None
    order_type: Optional[int] = None
    order_desc: Optional[str] = None
    step_count: Optional[int] = None
    sign: Optional[str] = None


class OrdersDto(BaseDto):
    """DTO для отображения поручения"""

    order_date: date
    order_deadline: Optional[date] = None
    order_num: Optional[int] = None
    employee_id: Optional[int] = None
    order_status: Optional[int] = None
    order_type: Optional[int] = None
    order_desc: Optional[str] = None
    step_count: Optional[int] = None
    sign: Optional[str] = None

    # Relationships
    order_status_ref: Optional[DicOrderStatusDto] = None
    order_type_ref: Optional[DicOrderTypeDto] = None


class OrdersFilterDto(BasestDto):
    """DTO для фильтрации поручений"""

    order_date_from: Optional[date] = None
    order_date_to: Optional[date] = None
    order_deadline_from: Optional[date] = None
    order_deadline_to: Optional[date] = None
    order_num: Optional[int] = None
    employee_id: Optional[int] = None
    order_status: Optional[int] = None
    order_type: Optional[int] = None
