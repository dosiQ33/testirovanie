from typing import Optional
from app.modules.common.dto import BasestDto
from app.modules.ckf.dtos import OrganizationDto, KkmsDto


class GtinNpDto(BasestDto):
    """DTO для GTIN по налогоплательщикам"""

    id: int
    dtype: Optional[str] = None
    org_id: Optional[int] = None
    gtin: Optional[str] = None
    item_name: Optional[str] = None
    full_price: Optional[float] = None
    full_count: Optional[float] = None


class GtinKkmsDto(BasestDto):
    """DTO для GTIN по ККМ"""

    id: int
    dtype: Optional[str] = None
    kkms_id: Optional[int] = None
    gtin: Optional[str] = None
    item_name: Optional[str] = None
    full_price: Optional[float] = None
    full_count: Optional[float] = None


class GtinNpFilterDto(BasestDto):
    """DTO для фильтрации GTIN по налогоплательщикам"""

    dtype: Optional[str] = None
    org_id: Optional[int] = None
    gtin: Optional[str] = None


class GtinKkmsFilterDto(BasestDto):
    """DTO для фильтрации GTIN по ККМ"""

    dtype: Optional[str] = None
    kkms_id: Optional[int] = None
    gtin: Optional[str] = None


class GtinTotalDto(BasestDto):
    """DTO для GTIN общей статистики"""

    id: int
    dtype: Optional[str] = None
    kkms_id: Optional[int] = None
    gtin: Optional[str] = None
    item_name: Optional[str] = None
    full_price: Optional[float] = None
    full_count: Optional[float] = None


class GtinTotalFilterDto(BasestDto):
    """DTO для фильтрации GTIN общей статистики"""

    dtype: Optional[str] = None
    kkms_id: Optional[int] = None
    gtin: Optional[str] = None
