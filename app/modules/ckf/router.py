"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from datetime import datetime
from loguru import logger
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit, get_session_without_commit
from app.modules.common.dto import Bbox, CountResponseDto, CountByTerritoryAndRegionsDto, ByYearAndRegionsFilterDto, CountByYearAndRegionsDto
from app.modules.common.router import BaseCRUDRouter, ORJsonCoder, request_key_builder, cache_ttl
from app.modules.common.mappers import to_regions_filter_dto
from .dtos import (
    EsfSellerBuyerDto,
    EsfSellerBuyerSimpleDto,
    FnoDto,
    FnoStatisticsDto,
    FnoBarChartDto,
    FnoBarChartItemDto,
    GetReceiptByFiscalBinDto,
    GetReceiptByFiscalKkmRegNumberDto,
    GetReceiptByFiscalKkmSerialNumberDto,
    KkmsByTerritorySumByMonthDto,
    KkmsDto,
    KkmsFilterDto,
    OrganizationDto,
    OrganizationsFilterDto,
    OrganizationsByYearAndRegionsResponseDto,
    ReceiptsAnnualDto,
    ReceiptsDailyDto,
    ReceiptsDto,
    RiskInfosDto,
    EsfStatisticsDto,
    EsfMonthDto,
    EsfMontlyStatisticsDto
)
from .repository import (
    EsfBuyerDailyRepo,
    EsfBuyerRepo,
    EsfSellerDailyRepo,
    EsfSellerRepo,
    FnoRepo,
    KkmsRepo,
    OrganizationsRepo,
    ReceiptsAnnualRepo,
    ReceiptsDailyRepo,
    ReceiptsRepo,
    RiskInfosRepo,
    EsfStatisticsRepo
)
from .models import EsfBuyer, EsfBuyerDaily, EsfSeller, EsfSellerDaily, Organizations, Kkms, Receipts, RiskInfos  # noqa
from .mappers import to_organization_count_by_regions_response
from datetime import date

router = APIRouter(prefix="/ckf")


class OrganizationsRouter(APIRouter):
    sub_router = APIRouter(prefix="/organizations", tags=["ckf: organizations"])
    base_router = BaseCRUDRouter("organizations", Organizations, OrganizationsRepo, OrganizationDto, tags=["ckf: organizations"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def filter(
        filters: Annotated[OrganizationsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await OrganizationsRepo(session).filter(filters)
        return [OrganizationDto.model_validate(item) for item in response]

    @sub_router.get("/bbox")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_bbox(bbox: Annotated[Bbox, Query()], session: AsyncSession = Depends(get_session_with_commit)):
        response = await OrganizationsRepo(session).get_by_bbox(bbox)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Произошла ошибка при поиске записей")

        return response

    @sub_router.get("/branches/{bin_root}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_branches(
        bin_root: str,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[OrganizationDto]:
        response = await OrganizationsRepo(session).get_branches(bin_root)

        return [OrganizationDto.model_validate(item) for item in response]

    @sub_router.get("/{id}/kkms")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_kkms(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[KkmsDto]:
        return await OrganizationsRepo(session).get_kkms(id)
        # return [KkmsDto.model_validate(kkm) for kkm in kkms]

    @sub_router.get("/{id}/fno")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_fno(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[FnoDto]:
        response = await FnoRepo(session).get_many_by_organization_id(id)
        if not response:
            return []

        return [FnoDto.model_validate(item) for item in response]

    @sub_router.get("/{id}/esf-seller-buyer")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_esf_seller_buyer(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        esf_seller = await EsfSellerRepo(session).get_by_organization_id(id)
        esf_seller_daily = await EsfSellerDailyRepo(session).get_by_organization_id(id)
        esf_buyer = await EsfBuyerRepo(session).get_by_organization_id(id)
        esf_buyer_daily = await EsfBuyerDailyRepo(session).get_by_organization_id(id)

        return {
            "esf_seller": EsfSellerBuyerSimpleDto.model_validate(esf_seller) if esf_seller else None,
            "esf_seller_daily": EsfSellerBuyerSimpleDto.model_validate(esf_seller_daily) if esf_seller_daily else None,
            "esf_buyer": EsfSellerBuyerSimpleDto.model_validate(esf_buyer) if esf_buyer else None,
            "esf_buyer_daily": EsfSellerBuyerSimpleDto.model_validate(esf_buyer_daily) if esf_buyer_daily else None,
        }

    @sub_router.get("/{id}/kkms/summary")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_kkms_summary(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        kkms = await OrganizationsRepo(session).get_kkms(id)

        date = datetime.now().date()
        year = date.year

        date_str = date.strftime("%Y-%m-%d")

        logger.info(f"date: {date_str}")

        kkms_summary = []

        for kkm in kkms:
            receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(kkm.id, date)
            receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(kkm.id, year)

            kkms_summary.append(
                {
                    "kkm": KkmsDto.model_validate(kkm),
                    "receipts_daily": ReceiptsDailyDto.model_validate(receipts_daily) if receipts_daily else None,
                    "receipts_annual": ReceiptsAnnualDto.model_validate(receipts_annual) if receipts_annual else None,
                }
            )

        return kkms_summary

    @sub_router.get("/territory/esf-summary")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_territory_esf_summary(
        filters: Annotated[OrganizationsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        summary = []

        organizations = await OrganizationsRepo(session).filter(filters)
        orgs = [OrganizationDto.model_validate(item) for item in organizations]

        for org in orgs:
            esf_seller = await EsfSellerRepo(session).get_by_organization_id(org.id)
            esf_seller_daily = await EsfSellerDailyRepo(session).get_by_organization_id(org.id)
            esf_buyer = await EsfBuyerRepo(session).get_by_organization_id(org.id)
            esf_buyer_daily = await EsfBuyerDailyRepo(session).get_by_organization_id(org.id)

            item_summary = {
                "organization": org,
                "esf": {
                    "esf_seller": EsfSellerBuyerSimpleDto.model_validate(esf_seller) if esf_seller else None,
                    "esf_seller_daily": EsfSellerBuyerSimpleDto.model_validate(esf_seller_daily) if esf_seller_daily else None,
                    "esf_buyer": EsfSellerBuyerSimpleDto.model_validate(esf_buyer) if esf_buyer else None,
                    "esf_buyer_daily": EsfSellerBuyerSimpleDto.model_validate(esf_buyer_daily) if esf_buyer_daily else None,
                },
            }

            summary.append(item_summary)

        return summary
    
    @sub_router.get('/count/monthly/by-year-regions', response_model=OrganizationsByYearAndRegionsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа    
    async def count_monthly_by_regions(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
          
        is_current_year = (count_dto.year == date.today().year)
        filters = to_regions_filter_dto(count_dto=count_dto, is_current_year=is_current_year)
        
        rows = await OrganizationsRepo(session).count_monthly_by_year_and_regions(filters=filters)
        
        return to_organization_count_by_regions_response(rows=rows)

    @sub_router.get('/count/by-year-regions', response_model=CountResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа    
    async def count_by_regions(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
          
        is_current_year = (count_dto.year == date.today().year)
        date_ = date(count_dto.year, 12, 31) if not is_current_year else None

        count = await OrganizationsRepo(session).count_by_year_and_regions(
            count_dto=count_dto, date_=date_
        )
        
        return CountResponseDto(
            count=count
        )
        
            
class KkmsRouter(APIRouter):
    sub_router = APIRouter(prefix="/kkms", tags=["ckf: kkms"])
    base_router = BaseCRUDRouter("kkms", Kkms, KkmsRepo, KkmsDto, tags=["ckf: kkms"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/bbox")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_bbox(bbox: Annotated[Bbox, Query()], session: AsyncSession = Depends(get_session_with_commit)):
        response = await KkmsRepo(session).get_by_bbox(bbox)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Произошла ошибка при поиске записей")

        return response

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def filter(
        filters: Annotated[KkmsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await KkmsRepo(session).filter(filters)
        return [KkmsDto.model_validate(item) for item in response]

    @sub_router.get("/{id}/receipts-summary")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_kkms_summary(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        date = datetime.now().date()
        year = date.year

        date_str = date.strftime("%Y-%m-%d")

        logger.info(f"date: {date_str}")

        receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(id, date)
        receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(id, year)

        return {
            "receipts_daily": ReceiptsDailyDto.model_validate(receipts_daily) if receipts_daily else None,
            "receipts_annual": ReceiptsAnnualDto.model_validate(receipts_annual) if receipts_annual else None,
        }

    @sub_router.get("/territory/receipts-summary")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_territory_receipts_summary(
        filters: Annotated[KkmsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        summary = []

        date = datetime.now().date()
        year = date.year

        kkms_unvalidated = await KkmsRepo(session).filter(filters)
        kkms = [KkmsDto.model_validate(item) for item in kkms_unvalidated]

        for kkm in kkms:
            receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(kkm.id, date)
            receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(kkm.id, year)

            item_summary = {
                "kkm": kkm,
                "receipts_daily": ReceiptsDailyDto.model_validate(receipts_daily) if receipts_daily else None,
                "receipts_annual": ReceiptsAnnualDto.model_validate(receipts_annual) if receipts_annual else None,
            }

            summary.append(item_summary)

        return summary

    @sub_router.get("/territory/receipts-sum-by-month")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_territory_receipts_totals(
        dto: Annotated[KkmsByTerritorySumByMonthDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        filters = KkmsFilterDto(territory=dto.territory)

        kkms_unvalidated = await KkmsRepo(session).filter(filters)
        kkms = [KkmsDto.model_validate(item) for item in kkms_unvalidated]
        kkm_ids = [kkm.id for kkm in kkms]

        monthly = await ReceiptsDailyRepo(session).get_sum_by_month_kkms(kkm_ids, dto.year)

        # return jsonable response
        monthly = [
            {
                "year": dto.year,
                "month": month,
                "check_sum": check_sum,
                "check_count": check_count,
            }
            for month, check_sum, check_count in monthly
        ]

        return monthly
    

class FnoStatisticsRouter(APIRouter):
    sub_router = APIRouter(prefix="/fno-statistics", tags=["ckf: fno-statistics"])
    
    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    """Own routes"""
    
    @sub_router.get("count/aggregation/by-regions", response_model=FnoStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_fno_statistics(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        current_year = 2025 # как я понял пока будет возможность только посмотреть 2025-2024 года
        prev_year = 2024 
        
        result = await FnoRepo(session).get_fno_aggregation_statistics(
            filters=count_dto,
            current_year=current_year,
            prev_year=prev_year
        )
        
        return FnoStatisticsDto(**result._mapping)

    @sub_router.get("/bar-chart", response_model=FnoBarChartDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_fno_bar_chart(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Get FNO data by individual fields for bar chart visualization"""
        prev_year = 2024  # Previous year as specified
        
        chart_data = await FnoRepo(session).get_fno_bar_chart_data(
            filters=count_dto,
            year=prev_year
        )
        
        return FnoBarChartDto(
            title="Оборот по ФНО за предыдущий год",
            year=prev_year,
            data=[FnoBarChartItemDto(**item) for item in chart_data]
        )


class EsfSellerRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-seller", tags=["ckf: esf-seller"])
    base_router = BaseCRUDRouter("esf-seller", EsfSeller, EsfSellerRepo, EsfSellerBuyerDto, tags=["ckf: esf-seller"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/organization/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_organization_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[EsfSellerBuyerDto]:
        return await EsfSellerRepo(session).get_by_organization_id(id)


class EsfSellerDailyRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-seller-daily", tags=["ckf: esf-seller-daily"])
    base_router = BaseCRUDRouter(
        "esf-seller-daily", EsfSellerDaily, EsfSellerDailyRepo, EsfSellerBuyerDto, tags=["ckf: esf-seller-daily"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/organization/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_organization_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[EsfSellerBuyerDto]:
        return await EsfSellerRepo(session).get_by_organization_id(id)


class EsfBuyerRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-buyer", tags=["ckf: esf-buyer"])
    base_router = BaseCRUDRouter("esf-buyer", EsfBuyer, EsfBuyerRepo, EsfSellerBuyerDto, tags=["ckf: esf-buyer"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/organization/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_organization_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[EsfSellerBuyerDto]:
        return await EsfSellerRepo(session).get_by_organization_id(id)


class EsfBuyerDailyRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-buyer-daily", tags=["ckf: esf-buyer-daily"])
    base_router = BaseCRUDRouter(
        "esf-buyer-daily", EsfBuyerDaily, EsfBuyerDailyRepo, EsfSellerBuyerDto, tags=["ckf: esf-buyer-daily"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/organization/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_organization_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[EsfSellerBuyerDto]:
        return await EsfSellerRepo(session).get_by_organization_id(id)


class EsfStatisticsRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-statistics", tags=["ckf: esf-statistics"])
    
    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    """Own routes"""

    @sub_router.get("count/aggregation/by-regions", response_model=EsfStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_esf_statistics(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        result = await EsfStatisticsRepo(session).get_esf_statistics(count_dto)
        
        return EsfStatisticsDto(
            esf_seller_daily_amount=result["esf_seller_daily"].turnover,
            esf_seller_amount=result["esf_seller"].turnover,
            esf_buyer_daily_amount=result["esf_buyer_daily"].turnover,
            esf_buyer_amount=result["esf_buyer"].turnover
        )

    @sub_router.get("count/monthly/by-regions", response_model=EsfMontlyStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_esf_statistics(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        period_start = date(2025, 1, 1) # пока есть данные только за 2025 год
        period_end = date(2025, 12, 1)
        
        filters = ByYearAndRegionsFilterDto(
            territory=count_dto.territory,
            period_start=period_start,
            period_end=period_end,
            region=count_dto.region
        )
                
        result = await EsfStatisticsRepo(session).get_esf_statistics_monthly(filters=filters)
        
        return EsfMontlyStatisticsDto(
            esf_seller_monthly=[EsfMonthDto(month=item["date_"].month, turnover=item["turnover"]) for item in result["esf_seller_month"]],
            esf_buyer_montly=[EsfMonthDto(month=item["date_"].month, turnover=item["turnover"]) for item in result["esf_buyer_month"]]
        )


class RiskInfosRouter(APIRouter):
    sub_router = APIRouter(prefix="/risk-infos", tags=["ckf: risk-infos"])
    base_router = BaseCRUDRouter("risk-infos", RiskInfos, RiskInfosRepo, RiskInfosDto, tags=["ckf: risk-infos"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/organization/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_by_organization_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> RiskInfosDto:
        response = await RiskInfosRepo(session).get_latest_by_organization_id(id)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сведения по рискам не найдены")
        return RiskInfosDto.model_validate(response)


class ReceiptsRouter(APIRouter):
    sub_router = APIRouter(prefix="/receipts", tags=["ckf: receipts"])
    # base_router = BaseCRUDRouter("receipts", Receipts, ReceiptsRepo, ReceiptsDto, tags=["ckf: receipts"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        # self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/fiskal-kkm-reg-number")
    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_by_fiscal_and_kkm_reg_number(
        dto: Annotated[GetReceiptByFiscalKkmRegNumberDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsDto]:
        response = await ReceiptsRepo(session).get_by_fiscal_and_kkm_reg_number(
            fiskal_sign=dto.fiskal_sign, kkm_reg_number=dto.kkm_reg_number
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чек не найден по указанному фискальному признаку и регистрационному номеру ККМ",
            )
        return [ReceiptsDto.model_validate(item) for item in response]

    @sub_router.get("/fiskal-kkm-serial-number")
    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_by_fiscal_and_kkm_serial_number(
        dto: Annotated[GetReceiptByFiscalKkmSerialNumberDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsDto]:
        response = await ReceiptsRepo(session).get_by_fiscal_and_kkm_serial_number(
            fiskal_sign=dto.fiskal_sign, kkm_serial_number=dto.kkm_serial_number
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чек не найден по указанному фискальному признаку и серийному номеру ККМ",
            )
        return [ReceiptsDto.model_validate(item) for item in response]

    @sub_router.get("/fiskal-kkm-iin-bin")
    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_by_fiscal_and_iin_bin(
        dto: Annotated[GetReceiptByFiscalBinDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsDto]:
        response = await ReceiptsRepo(session).get_by_fiscal_and_iin_bin(fiskal_sign=dto.fiskal_sign, kkm_iin_bin=dto.iin_bin)

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чек не найден по указанному фискальному признаку и ИИН/БИН",
            )
        return [ReceiptsDto.model_validate(item) for item in response]
    

router.include_router(OrganizationsRouter())
router.include_router(KkmsRouter())
router.include_router(ReceiptsRouter())
router.include_router(FnoStatisticsRouter())

router.include_router(EsfSellerRouter())
router.include_router(EsfSellerDailyRouter())
router.include_router(EsfBuyerRouter())
router.include_router(EsfBuyerDailyRouter())
router.include_router(EsfStatisticsRouter())

router.include_router(RiskInfosRouter())