"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from datetime import date, datetime
from pydantic import Field, ConfigDict, field_serializer
from typing import Any, List, Optional


from app.modules.common.dto import (
    BasestDto,
    DtoWithShape,
    BaseDto,
    ByMonthAndRegionsResponseDto,
)
from app.modules.ext.okeds.dtos import OkedsDto
from app.modules.nsi.dtos import CommonRefDto, SimpleRefDto


class KkmsDto(DtoWithShape):
    organization_id: int

    reg_number: str

    serial_number: Optional[str]
    model_name: Optional[str]
    made_year: Optional[str]

    date_start: Optional[date]
    date_stop: Optional[date]

    address: Optional[str]

    model_config = ConfigDict(protected_namespaces=())


class OrganizationDto(DtoWithShape):
    iin_bin: str
    name_ru: str
    name_kk: Optional[str]
    date_start: Optional[date]
    date_stop: Optional[date]

    ugd_id: Optional[int]
    ugd: Optional[CommonRefDto] = None

    oked_id: Optional[int]
    oked: Optional[OkedsDto] = None

    nds_number: Optional[int]
    nds_date_reg: Optional[datetime] = None

    tax_regime_id: Optional[int]
    tax_regime: Optional[SimpleRefDto] = None

    reg_type_id: Optional[int]
    reg_type: Optional[SimpleRefDto] = None

    knn: Optional[float] = None
    knn_co: Optional[float] = None

    bin_root: Optional[str] = None
    jur_fiz: Optional[int] = None

    leader_id: Optional[int]
    leader: Optional[SimpleRefDto] = None

    address: Optional[str]

    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None

    kkms: List[KkmsDto] = Field(default_factory=list)


class OrganizationsWithKkmsDto(OrganizationDto):
    kkms: List[KkmsDto] = Field(default_factory=list)


class OrganizationsFilterDto(BasestDto):
    territory: Optional[str] = None
    iin_bin: Optional[str] = None
    risk_degree_ids: Optional[List[int]] = None
    oked_ids: Optional[List[int]] = None


class OrganizationsByYearAndRegionsResponseDto(BasestDto):
    monthly: List[ByMonthAndRegionsResponseDto]
    year_count: Optional[int]


class KkmsWithOrganizationDto(KkmsDto):
    organization: OrganizationDto


class KkmsFilterDto(BasestDto):
    territory: Optional[str] = None
    reg_number: Optional[str] = None


class KkmsByTerritorySumByMonthDto(BasestDto):
    territory: str
    year: int


class FnoTypesDto(BaseDto):
    id: int
    name: str


class FnoDto(BaseDto):
    id: int

    organization_id: int

    type_id: int
    type: FnoTypesDto

    year: int

    fno_100_00: Optional[float] = None
    fno_110_00: Optional[float] = None
    fno_150_00: Optional[float] = None
    fno_180_00: Optional[float] = None
    fno_220_00: Optional[float] = None
    fno_300_00: Optional[float] = None
    fno_910_00: Optional[float] = None
    fno_911_00: Optional[float] = None
    fno_912_00: Optional[float] = None
    fno_913_00: Optional[float] = None
    fno_920_00: Optional[float] = None


class FnoStatisticsDto(BasestDto):
    turnover_current_year: float
    turnover_prev_year: float


class FnoBarChartItemDto(BasestDto):
    fno_code: str
    amount: float


class FnoBarChartDto(BasestDto):
    title: str
    year: int
    data: List[FnoBarChartItemDto]


class RiskInfosDto(BaseDto):
    organization_id: int
    # organization: OrganizationDto

    risk_degree_id: int
    risk_degree: SimpleRefDto

    calculated_at: date

    ugd_id: int
    ugd: Optional[CommonRefDto] = None


class PersonsDto(BaseDto):
    iin: str
    name: str

    organizations: List[OrganizationDto] = Field(default_factory=list)


class EsfSellerBuyerSimpleDto(BaseDto):
    organization_id: Optional[int] = None

    total_amount: Optional[float] = None
    nds_amount: Optional[float] = None


class EsfSellerBuyerDto(BaseDto):
    organization_id: int
    organization: OrganizationDto

    total_amount: float
    nds_amount: float


class EsfMonthDto(BasestDto):
    month: int
    turnover: float


class EsfStatisticsDto(BasestDto):
    esf_seller_daily_amount: float
    esf_seller_amount: float
    esf_buyer_daily_amount: float
    esf_buyer_amount: float


class EsfMontlyStatisticsDto(BasestDto):
    esf_seller_monthly: List[EsfMonthDto]
    esf_buyer_montly: List[EsfMonthDto]


class OrganizationEsfSellerBuyerDto(BaseDto):
    esf_seller: Optional[EsfSellerBuyerSimpleDto] = Field(default_factory=list)
    esf_seller_daily: Optional[EsfSellerBuyerSimpleDto] = Field(default_factory=list)
    esf_buyer: Optional[EsfSellerBuyerSimpleDto] = Field(default_factory=list)
    esf_buyer_daily: Optional[EsfSellerBuyerSimpleDto] = Field(default_factory=list)


class ReceiptsDto(BaseDto):
    kkms_id: int
    kkm: Optional[KkmsDto] = Field()

    operation_date: Optional[datetime]
    auto_fiskal_mark_check: Optional[str]
    fiskal_sign: Optional[int] = Field()
    item_name: Optional[str]
    item_price: Optional[float]
    item_count: Optional[int]
    item_nds: Optional[float]
    full_item_price: Optional[float]
    payment_type: Optional[int]
    # updated_date: Optional[datetime]

    @field_serializer("fiskal_sign")
    def serialize_country(self, fiskal_sign: Any, _info):
        return fiskal_sign


class ReceiptsAnnualDto(BaseDto):
    kkms_id: int
    # kkm: KkmsDto

    check_sum: float
    check_count: int
    year: int


class ReceiptsDailyDto(BaseDto):
    kkms_id: int
    # kkm: KkmsDto

    check_sum: float
    check_count: int
    date_check: date


class ReceiptsSummaryDto(BaseDto):
    kkms_id: int

    check_sum: float
    check_count: int


class GetReceiptByFiscalKkmRegNumberDto(BasestDto):
    fiskal_sign: int = Field()
    kkm_reg_number: str

    @field_serializer("fiskal_sign")
    def serialize_country(self, fiskal_sign: Any, _info):
        return fiskal_sign


class GetReceiptByFiscalKkmSerialNumberDto(BasestDto):
    fiskal_sign: int = Field()
    kkm_serial_number: str

    @field_serializer("fiskal_sign")
    def serialize_country(self, fiskal_sign: Any, _info):
        return fiskal_sign


class GetReceiptByFiscalBinDto(BasestDto):
    fiskal_sign: int = Field()
    iin_bin: str

    @field_serializer("fiskal_sign")
    def serialize_country(self, fiskal_sign: Any, _info):
        return fiskal_sign
