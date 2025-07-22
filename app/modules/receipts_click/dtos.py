from typing import Optional, List
from datetime import datetime
from pydantic import Field
from app.modules.common.dto import BasestDto, BaseDto
from app.modules.ckf.dtos import (
    OrganizationDto,
)


class KkmsClickDto(BasestDto):
    """DTO для ККМ из ClickHouse"""

    id: Optional[int] = None
    organization_id: Optional[int] = None
    reg_number: Optional[str] = None
    serial_number: Optional[str] = None
    model_name: Optional[str] = None
    made_year: Optional[str] = None
    date_start: Optional[datetime] = None
    date_stop: Optional[datetime] = None
    address: Optional[str] = None
    shape: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReceiptsClickDto(BasestDto):
    """DTO для чеков из ClickHouse (таблица testr)"""

    kkms_id: int
    operation_date: datetime
    auto_fiskal_mark_check: Optional[str] = None
    fiskal_sign: Optional[str] = None
    item_name: str
    item_price: Optional[float] = None
    item_count: Optional[float] = None
    item_nds: Optional[float] = None
    full_item_price: Optional[float] = None
    payment_type: str
    updated_date: datetime
    pay: List[str] = Field(default_factory=list)
    pos: str


class ReceiptsWithKkmDto(ReceiptsClickDto):
    """DTO для чеков с информацией о ККМ и опционально об организации"""

    kkm: Optional[KkmsClickDto] = None
    organization: Optional[OrganizationDto] = None


class ReceiptsFilterDto(BasestDto):
    """DTO для фильтрации чеков"""

    kkms_id: Optional[int] = None
    organization_id: Optional[int] = None
    reg_number: Optional[str] = None
    serial_number: Optional[str] = None
    fiskal_sign: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    item_name: Optional[str] = None
    payment_type: Optional[str] = None
    pos: Optional[str] = None


class ReceiptsStatsDto(BasestDto):
    """DTO для статистики по чекам"""

    total_receipts: int
    total_amount: float
    avg_amount: float
    min_amount: float
    max_amount: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class GetReceiptByFiscalKkmRegNumberClickDto(BasestDto):
    """DTO для поиска чека по фискальному признаку и регистрационному номеру ККМ"""

    fiskal_sign: str = Field()
    kkm_reg_number: str


class GetReceiptByFiscalKkmSerialNumberClickDto(BasestDto):
    """DTO для поиска чека по фискальному признаку и серийному номеру ККМ"""

    fiskal_sign: str = Field()
    kkm_serial_number: str


class GetReceiptByFiscalOrganizationClickDto(BasestDto):
    """DTO для поиска чека по фискальному признаку и ID организации"""

    fiskal_sign: str = Field()
    organization_id: int
