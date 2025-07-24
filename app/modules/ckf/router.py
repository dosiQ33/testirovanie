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
from app.modules.common.dto import (
    Bbox,
    CountResponseDto,
    CountByTerritoryAndRegionsDto,
    ByYearAndRegionsFilterDto,
    CountByYearAndRegionsDto,
    TerritoryFilterDto,
)
from app.modules.common.enums import RegionEnum
from app.modules.common.router import (
    BaseCRUDRouter,
    ORJsonCoder,
    request_key_builder,
    cache_ttl,
)
from app.modules.common.mappers import to_regions_filter_dto
from app.modules.common.utils import territory_to_geo_element
from .dtos import (
    EsfSellerBuyerDto,
    EsfSellerBuyerSimpleDto,
    EsfMonthlyByBuildingRequestDto,
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
    EsfMontlyStatisticsDto,
    EsfMonthlyStatisticsRequestDto,
    KkmStatisticsRequestDto,
    KkmMonthlyStatisticsItemDto,
    KkmStatisticsResponseDto,
    KkmAggregatedStatisticsRequestDto,
    KkmAggregatedStatisticsResponseDto,
    OrganizationsAndKkmsCountResponseDto,
    BuildingsFilterDto,
    KkmAggregatedByBuildingResponseDto,
    NPBuildingListResponseDto,
    EsfBuildingListResponseDto,
    FnoBuildingsBarChartListResponseDto,
    FnoInfoListDto,
    KkmsInfoListDto,
    SzptDto,
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
    EsfStatisticsRepo,
    SzptRepo,
)
from .models import (
    EsfBuyer,
    EsfBuyerDaily,
    EsfSeller,
    EsfSellerDaily,
    Organizations,
    Kkms,
    Receipts,
    RiskInfos,
    DicSzpt,
)  # noqa
from .mappers import to_organization_count_by_regions_response
from datetime import date

router = APIRouter(prefix="/ckf")


class OrganizationsRouter(APIRouter):
    sub_router = APIRouter(prefix="/organizations", tags=["ckf: organizations"])
    base_router = BaseCRUDRouter(
        "organizations",
        Organizations,
        OrganizationsRepo,
        OrganizationDto,
        tags=["ckf: organizations"],
    )

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
    async def get_by_bbox(
        bbox: Annotated[Bbox, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await OrganizationsRepo(session).get_by_bbox(bbox)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Произошла ошибка при поиске записей",
            )

        return response

    @sub_router.get("/branches/{bin_root}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_branches(
        bin_root: str,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[OrganizationDto]:
        response = await OrganizationsRepo(session).get_branches(bin_root)

        return [OrganizationDto.model_validate(item) for item in response]

    @sub_router.get("/buildings")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_organizations_in_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        organizations = await OrganizationsRepo(
            session
        ).get_all_organizations_by_building(filters)
        kkms = await KkmsRepo(session).get_kkms_in_building(filters)

        return OrganizationsAndKkmsCountResponseDto(
            organizations=organizations, kkms=kkms
        )

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
            "esf_seller": (
                EsfSellerBuyerSimpleDto.model_validate(esf_seller)
                if esf_seller
                else None
            ),
            "esf_seller_daily": (
                EsfSellerBuyerSimpleDto.model_validate(esf_seller_daily)
                if esf_seller_daily
                else None
            ),
            "esf_buyer": (
                EsfSellerBuyerSimpleDto.model_validate(esf_buyer) if esf_buyer else None
            ),
            "esf_buyer_daily": (
                EsfSellerBuyerSimpleDto.model_validate(esf_buyer_daily)
                if esf_buyer_daily
                else None
            ),
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
            receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(kkm.id)
            receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(
                kkm.id, year
            )

            kkms_summary.append(
                {
                    "kkm": KkmsDto.model_validate(kkm),
                    "receipts_daily": (
                        ReceiptsDailyDto.model_validate(receipts_daily)
                        if receipts_daily
                        else None
                    ),
                    "receipts_annual": (
                        ReceiptsAnnualDto.model_validate(receipts_annual)
                        if receipts_annual
                        else None
                    ),
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
            esf_seller_daily = await EsfSellerDailyRepo(session).get_by_organization_id(
                org.id
            )
            esf_buyer = await EsfBuyerRepo(session).get_by_organization_id(org.id)
            esf_buyer_daily = await EsfBuyerDailyRepo(session).get_by_organization_id(
                org.id
            )

            item_summary = {
                "organization": org,
                "esf": {
                    "esf_seller": (
                        EsfSellerBuyerSimpleDto.model_validate(esf_seller)
                        if esf_seller
                        else None
                    ),
                    "esf_seller_daily": (
                        EsfSellerBuyerSimpleDto.model_validate(esf_seller_daily)
                        if esf_seller_daily
                        else None
                    ),
                    "esf_buyer": (
                        EsfSellerBuyerSimpleDto.model_validate(esf_buyer)
                        if esf_buyer
                        else None
                    ),
                    "esf_buyer_daily": (
                        EsfSellerBuyerSimpleDto.model_validate(esf_buyer_daily)
                        if esf_buyer_daily
                        else None
                    ),
                },
            }

            summary.append(item_summary)

        return summary

    @sub_router.get(
        "/count/monthly/by-year-regions",
        response_model=OrganizationsByYearAndRegionsResponseDto,
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def count_monthly_by_regions(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):

        is_current_year = count_dto.year == date.today().year
        filters = to_regions_filter_dto(
            count_dto=count_dto, is_current_year=is_current_year
        )

        rows = await OrganizationsRepo(session).count_monthly_by_year_and_regions(
            filters=filters
        )

        return to_organization_count_by_regions_response(rows=rows)

    @sub_router.get("/count/by-year-regions", response_model=CountResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def count_by_regions(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):

        is_current_year = count_dto.year == date.today().year
        date_ = date(count_dto.year, 12, 31) if not is_current_year else None

        count = await OrganizationsRepo(session).count_by_year_and_regions(
            count_dto=count_dto, date_=date_
        )

        return CountResponseDto(count=count)

    @sub_router.get("/info/by-building", response_model=NPBuildingListResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_organizations_info_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await OrganizationsRepo(session).get_organizations_info_by_building(
            filters
        )

        return {"info": response}


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
    async def get_by_bbox(
        bbox: Annotated[Bbox, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await KkmsRepo(session).get_by_bbox(bbox)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Произошла ошибка при поиске записей",
            )

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

        receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(id)
        receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(id, year)

        return {
            "receipts_daily": (
                ReceiptsDailyDto.model_validate(receipts_daily)
                if receipts_daily
                else None
            ),
            "receipts_annual": (
                ReceiptsAnnualDto.model_validate(receipts_annual)
                if receipts_annual
                else None
            ),
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
            receipts_daily = await ReceiptsDailyRepo(session).get_by_date_kkm_id(kkm.id)
            receipts_annual = await ReceiptsAnnualRepo(session).get_by_year_kkm_id(
                kkm.id, year
            )

            item_summary = {
                "kkm": kkm,
                "receipts_daily": (
                    ReceiptsDailyDto.model_validate(receipts_daily)
                    if receipts_daily
                    else None
                ),
                "receipts_annual": (
                    ReceiptsAnnualDto.model_validate(receipts_annual)
                    if receipts_annual
                    else None
                ),
            }

            summary.append(item_summary)

        return summary

    @sub_router.get("/statistics", response_model=KkmStatisticsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_kkm_statistics(
        statistics_dto: Annotated[KkmStatisticsRequestDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):

        monthly_data = await ReceiptsRepo(session).get_monthly_statistics_by_territory(
            filters=statistics_dto
        )

        monthly_statistics = [
            KkmMonthlyStatisticsItemDto(
                month=int(month),
                receipts_count=int(receipts_count),
                turnover=float(turnover) if turnover else 0.0,
            )
            for month, receipts_count, turnover in monthly_data
        ]

        return KkmStatisticsResponseDto(monthly_data=monthly_statistics)

    @sub_router.get(
        "/aggregated-statistics", response_model=KkmAggregatedStatisticsResponseDto
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_kkm_aggregated_statistics(
        statistics_dto: Annotated[KkmAggregatedStatisticsRequestDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Get aggregated KKM statistics by territory"""
        # Валидация: для OBLAST и RAION territory обязателен
        if statistics_dto.region != RegionEnum.rk and not statistics_dto.territory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Territory parameter is required for region {statistics_dto.region.value}",
            )

        territory_wkt = (
            territory_to_geo_element(statistics_dto.territory)
            if statistics_dto.territory
            else None
        )
        current_date = datetime.now().date()

        result = await ReceiptsRepo(session).get_aggregated_statistics_by_territory(
            territory_wkt=territory_wkt, current_date=current_date
        )

        return KkmAggregatedStatisticsResponseDto(**result)

    @sub_router.get(
        "/aggregated-statistics-by-building",
        response_model=KkmAggregatedByBuildingResponseDto,
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_aggregated_statistics_by_buildings(
        statistics_dto: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        territory_wkt = territory_to_geo_element(statistics_dto.territory)
        current_date = datetime.now().date()

        result = await ReceiptsRepo(session).get_aggregated_statistics_by_building(
            territory=territory_wkt, current_date=current_date
        )

        return KkmAggregatedByBuildingResponseDto(**result)

    @sub_router.get("/monthly/by-building")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_monthly_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        result = await KkmsRepo(session).get_kkms_by_month(filters)
        return result

    @sub_router.get("/info/by-building", response_model=KkmsInfoListDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_info_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await KkmsRepo(session).get_kkm_info_by_building(filters)
        return response


class FnoStatisticsRouter(APIRouter):
    sub_router = APIRouter(prefix="/fno-statistics", tags=["ckf: fno-statistics"])

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    """Own routes"""

    @sub_router.get("/count/aggregation/by-regions", response_model=FnoStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_fno_statistics(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        current_year = (
            2025  # как я понял пока будет возможность только посмотреть 2025-2024 года
        )
        prev_year = 2024

        result = await FnoRepo(session).get_fno_aggregation_statistics(
            filters=count_dto, current_year=current_year, prev_year=prev_year
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
            filters=count_dto, year=prev_year
        )

        return FnoBarChartDto(
            title="Оборот по ФНО за предыдущий год",
            year=prev_year,
            data=[FnoBarChartItemDto(**item) for item in chart_data],
        )

    @sub_router.get(
        "/bar-chart/by-building", response_model=FnoBuildingsBarChartListResponseDto
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_fno_bar_chart_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):

        response = await FnoRepo(session).get_fno_bar_char_by_building(filters)
        return response

    @sub_router.get("/info/by-building", response_model=FnoInfoListDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_fno_info_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        result = await FnoRepo(session).get_fno_info_by_building(filters)

        return result


class EsfSellerRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-seller", tags=["ckf: esf-seller"])
    base_router = BaseCRUDRouter(
        "esf-seller",
        EsfSeller,
        EsfSellerRepo,
        EsfSellerBuyerDto,
        tags=["ckf: esf-seller"],
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


class EsfSellerDailyRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-seller-daily", tags=["ckf: esf-seller-daily"])
    base_router = BaseCRUDRouter(
        "esf-seller-daily",
        EsfSellerDaily,
        EsfSellerDailyRepo,
        EsfSellerBuyerDto,
        tags=["ckf: esf-seller-daily"],
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
    base_router = BaseCRUDRouter(
        "esf-buyer", EsfBuyer, EsfBuyerRepo, EsfSellerBuyerDto, tags=["ckf: esf-buyer"]
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


class EsfBuyerDailyRouter(APIRouter):
    sub_router = APIRouter(prefix="/esf-buyer-daily", tags=["ckf: esf-buyer-daily"])
    base_router = BaseCRUDRouter(
        "esf-buyer-daily",
        EsfBuyerDaily,
        EsfBuyerDailyRepo,
        EsfSellerBuyerDto,
        tags=["ckf: esf-buyer-daily"],
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

    @sub_router.get("/count/aggregation/by-regions", response_model=EsfStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_esf_statistics(
        count_dto: Annotated[CountByTerritoryAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        # Валидация: для OBLAST и RAION territory обязателен
        if count_dto.region != RegionEnum.rk and not count_dto.territory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Territory parameter is required for region {count_dto.region.value}",
            )

        result = await EsfStatisticsRepo(session).get_esf_statistics(count_dto)

        ###
        return EsfStatisticsDto(
            esf_seller_daily_amount=result["esf_seller_daily"]["turnover"],
            esf_seller_amount=result["esf_seller"]["turnover"],
            esf_buyer_daily_amount=result["esf_buyer_daily"]["turnover"],
            esf_buyer_amount=result["esf_buyer"]["turnover"],
        )

    @sub_router.get("/count/monthly/by-regions", response_model=EsfMontlyStatisticsDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_esf_monthly_statistics(
        statistics_dto: Annotated[EsfMonthlyStatisticsRequestDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        period_start = date(statistics_dto.year, 1, 1)
        period_end = date(statistics_dto.year, 12, 31)

        filters = ByYearAndRegionsFilterDto(
            territory=statistics_dto.territory,
            period_start=period_start,
            period_end=period_end,
            region=statistics_dto.region,
        )

        result = await EsfStatisticsRepo(session).get_esf_statistics_monthly(
            filters=filters
        )

        return EsfMontlyStatisticsDto(
            esf_seller_monthly=[
                EsfMonthDto(month=item["date_"].month, turnover=item["turnover"])
                for item in result["esf_seller_month"]
            ],
            esf_buyer_montly=[
                EsfMonthDto(month=item["date_"].month, turnover=item["turnover"])
                for item in result["esf_buyer_month"]
            ],
        )

    @sub_router.get("/info/by-building", response_model=EsfBuildingListResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_esf_info_by_building(
        filters: Annotated[BuildingsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await EsfStatisticsRepo(session).get_esf_info_by_building(filters)

        return {"info": response}


class RiskInfosRouter(APIRouter):
    sub_router = APIRouter(prefix="/risk-infos", tags=["ckf: risk-infos"])
    base_router = BaseCRUDRouter(
        "risk-infos", RiskInfos, RiskInfosRepo, RiskInfosDto, tags=["ckf: risk-infos"]
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
    ) -> RiskInfosDto:
        response = await RiskInfosRepo(session).get_latest_by_organization_id(id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сведения по рискам не найдены",
            )
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
    @cache(
        expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder
    )  # Кэширование на 24 часа
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
    @cache(
        expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder
    )  # Кэширование на 24 часа
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
    @cache(
        expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder
    )  # Кэширование на 24 часа
    async def get_by_fiscal_and_iin_bin(
        dto: Annotated[GetReceiptByFiscalBinDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsDto]:
        response = await ReceiptsRepo(session).get_by_fiscal_and_iin_bin(
            fiskal_sign=dto.fiskal_sign, kkm_iin_bin=dto.iin_bin
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чек не найден по указанному фискальному признаку и ИИН/БИН",
            )
        return [ReceiptsDto.model_validate(item) for item in response]
    
class SzptRouter(APIRouter):
    sub_router = APIRouter(prefix="/szpt-products", tags=["ckf: szpt"])
    base_router = BaseCRUDRouter('szpt-products', DicSzpt, SzptRepo, SzptDto, tags=["ckf: szpt"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get('/{product_id}/violations')
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_all_kkms_with_violations_by_szpt(
        product_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        
        response = await SzptRepo(session).get_all_kkms_with_violations_by_szpt(product_id)

        return response
    
    @sub_router.get('/info/{kkm_id}/{szpt_id}')
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_violations_count_by_kkm_id(
        kkm_id: int,
        szpt_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await SzptRepo(session).get_violations_count_by_kkm_id(kkm_id, szpt_id)

        return response


router.include_router(OrganizationsRouter())
router.include_router(KkmsRouter())
router.include_router(ReceiptsRouter())
router.include_router(FnoStatisticsRouter())

router.include_router(EsfSellerRouter())
router.include_router(EsfSellerDailyRouter())
router.include_router(EsfBuyerRouter())
router.include_router(EsfBuyerDailyRouter())
router.include_router(EsfStatisticsRouter())
router.include_router(SzptRouter())

router.include_router(RiskInfosRouter())
