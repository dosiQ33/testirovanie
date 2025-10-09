"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from app.modules.admins.models import Employees
from app.modules.nsi.dtos import SimpleRefDto
from fastapi import APIRouter, HTTPException, Query, status
from typing import Annotated, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from datetime import datetime
from loguru import logger
from fastapi_cache.decorator import cache
from geoalchemy2.elements import WKTElement

from math import ceil

from app.database.deps import get_session_with_commit, get_session_without_commit
from app.modules.common.dto import (
    Bbox,
    CountResponseDto,
    CountByTerritoryAndRegionsDto,
    ByYearAndRegionsFilterDto,
    CountByYearAndRegionsDto,
    TerritoryFilterDto,
)
from app.modules.common.territory_deps import (
    get_user_territory_info,
    get_user_territory_geom,
    UserTerritoryInfo,
)
from app.modules.common.enums import RegionEnum
from app.modules.admins.deps import get_current_employee
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
    OrganizationBboxDto,
    OrganizationDto,
    OrganizationWithRiskDto,
    OrganizationsFilterDto,
    OrganizationsByYearAndRegionsResponseDto,
    ReceiptsAnnualDto,
    ReceiptsDailyDto,
    ReceiptsDto,
    ReceiptsLatestFilterDto,
    RiskBboxDto,
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
    ProductsViolationDto,
    LastCheckViolationDto,
    ReceiptDetailDto,
    SzptRegionRequestDto,
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
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_bbox(
        bbox: Annotated[Bbox, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[OrganizationBboxDto]:
        """
        Получить организации в указанном bbox с информацией о рисках

        - **bbox**: координаты [minx, miny, maxx, maxy]
        - **srid**: система координат (по умолчанию 4326)

        Возвращает список организаций с рисками, включая справочную информацию:
        - Типы рисков
        - Степени рисков
        - Наименования рисков
        """
        response = await OrganizationsRepo(session).get_by_bbox(bbox)

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Произошла ошибка при поиске записей",
            )

        result = []
        for org in response:
            risks = [
                RiskBboxDto(
                    risk_type_id=risk["risk_type_id"],
                    risk_type_name=risk["risk_type_name"],
                    risk_degree_id=risk["risk_degree_id"],
                    risk_degree_name=risk["risk_degree_name"],
                    risk_name_id=risk["risk_name_id"],
                    risk_name_name=risk["risk_name_name"],
                    is_ordered=risk["is_ordered"],
                    risk_date=risk["risk_date"],
                )
                for risk in getattr(org, "_bbox_risks", [])
            ]

            result.append(
                OrganizationBboxDto(
                    id=org.id,
                    iin_bin=org.iin_bin,
                    name_ru=org.name_ru,
                    address=org.address,
                    shape=org.shape,
                    risks=risks,
                )
            )

        logger.info(f"Возвращено {len(result)} организаций с рисками для bbox.")
        return result

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
        esf_seller_daily = await EsfSellerDailyRepo(session).get_sum_by_organization_id(
            id
        )
        esf_buyer = await EsfBuyerRepo(session).get_by_organization_id(id)
        esf_buyer_daily = await EsfBuyerDailyRepo(session).get_sum_by_organization_id(
            id
        )

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
        kkms = await KkmsRepo(session).get_active_kkms_info(id)

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

    @sub_router.get(
        "/secure-filter",
        summary="Защищенный фильтр организаций с территориальным ограничением",
    )
    async def secure_filter_organizations(
        filters: Annotated[OrganizationsFilterDto, Query()],
        current_employee: Employees = Depends(get_current_employee),
        territory_info: UserTerritoryInfo = Depends(get_user_territory_info),
        user_territory_geom: WKTElement = Depends(get_user_territory_geom),
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[OrganizationDto]:
        """
        Получить организации с учетом территориальных прав доступа пользователя.

        Пользователь может видеть только организации в пределах своей территории:
        - Республиканский администратор: все организации РК
        - Областной сотрудник: только организации своей области
        - Районный сотрудник: только организации своего района

        **Дополнительные фильтры могут только сузить область поиска в рамках доступной территории.**

        - **territory**: дополнительный WKT полигон для фильтрации (должен быть в пределах доступной территории)
        - **iin_bin**: ИИН/БИН организации
        - **oked_ids**: список кодов ОКЭД
        - **risk_degree_ids**: список степеней риска
        """
        try:
            logger.info(
                f"Запрос организаций от пользователя {current_employee.login} "
                f"({territory_info.territory_level}: {territory_info.territory_name})"
            )

            if filters.territory and user_territory_geom is not None:
                repo = OrganizationsRepo(session)
                has_access = await repo.validate_user_territory_access(
                    filters.territory, user_territory_geom
                )

                if not has_access:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Нет доступа к указанной территории. "
                        f"Доступ ограничен: {territory_info.territory_name}",
                    )

            repo = OrganizationsRepo(session)
            organizations = await repo.filter_with_territory(
                filters=filters, user_territory_geom=user_territory_geom
            )

            logger.info(
                f"Возвращено {len(organizations)} организаций "
                f"для пользователя {current_employee.login}"
            )

            return [OrganizationDto.model_validate(item) for item in organizations]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при получении организаций для пользователя {current_employee.login}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера при получении данных",
            )

    @sub_router.get(
        "/my-territory-info", summary="Информация о территориальных правах доступа"
    )
    async def get_my_territory_info(
        current_employee: Employees = Depends(get_current_employee),
        territory_info: UserTerritoryInfo = Depends(get_user_territory_info),
    ) -> dict:
        """
        Получить информацию о территориальных правах доступа текущего пользователя
        """
        return {
            "employee_login": current_employee.login,
            "employee_position": current_employee.employee_position,
            "territory_level": territory_info.territory_level,
            "territory_name": territory_info.territory_name,
            "territory_id": territory_info.territory_id,
            "has_republic_access": territory_info.is_republic_level(),
            "description": {
                "republic": "Доступ ко всем данным Республики Казахстан",
                "oblast": f"Доступ только к данным {territory_info.territory_name}",
                "raion": f"Доступ только к данным {territory_info.territory_name}",
            }.get(territory_info.territory_level, "Неопределенный уровень доступа"),
        }

    @sub_router.get("/{id}/with-risks")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_organization_with_risks(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> OrganizationWithRiskDto:
        """
        Получить организацию по ID с подробной информацией о рисках
        """
        response = await OrganizationsRepo(session).get_one_by_id(id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Организация не найдена"
            )

        return OrganizationWithRiskDto.model_validate(response)


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

        return monthly_data

    @sub_router.get(
        "/aggregated-statistics", response_model=KkmAggregatedStatisticsResponseDto
    )
    # @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
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
    # @cache(expire=cache_ttl, key_builder=request_key_builder)
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

    @sub_router.get("/active-kkms/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_info_by_building(
        id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await KkmsRepo(session).get_active_kkms_count(id)
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
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):

        result = await FnoRepo(session).get_fno_aggregation_statistics(
            filters=count_dto
        )

        return FnoStatisticsDto(**result._mapping)

    @sub_router.get("/bar-chart", response_model=FnoBarChartDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_fno_bar_chart(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Get FNO data by individual fields for bar chart visualization"""
        prev_year = 2024  # Previous year as specified

        chart_data = await FnoRepo(session).get_fno_bar_chart_data(
            filters=count_dto,
        )

        return FnoBarChartDto(
            title="Оборот по ФНО за предыдущий год",
            year=count_dto.year,
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

    @sub_router.get("/latest-with-details")
    # @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_latest_receipts_with_details(
        limit: int = Query(
            100, ge=1, le=1000, description="Количество записей (от 1 до 1000)"
        ),
        kkm_id: Optional[int] = Query(None, description="ID ККМ для фильтрации"),
        organization_id: Optional[int] = Query(
            None, description="ID организации для фильтрации"
        ),
        include_today_filter: Optional[bool] = Query(
            True,
            description="Применять ли фильтр по сегодняшней дате (по умолчанию True)",
        ),
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[ReceiptDetailDto]:
        """
        Получить последние чеки с подробной информацией о ККМ и организации.

        - **limit**: количество записей для возврата (по умолчанию 100, максимум 1000)
        - **kkm_id**: ID ККМ для фильтрации (опционально)
        - **organization_id**: ID организации для фильтрации (опционально)
        - **include_today_filter**: применять ли фильтр по сегодняшней дате (по умолчанию True)

        Примеры использования:
        - Все сегодняшние чеки: `/latest-with-details?limit=50`
        - Чеки по ККМ: `/latest-with-details?kkm_id=123&include_today_filter=false`
        - Чеки по организации: `/latest-with-details?organization_id=456&include_today_filter=false`
        """
        # Создаем DTO из переданных параметров
        filters = ReceiptsLatestFilterDto(
            kkm_id=kkm_id,
            organization_id=organization_id,
            include_today_filter=include_today_filter,
        )

        response = await ReceiptsRepo(session).get_latest_receipts_with_details(
            limit=limit, filters=filters
        )

        return [ReceiptDetailDto.model_validate(item) for item in response]


class SzptRouter(APIRouter):
    sub_router = APIRouter(prefix="/szpt-products", tags=["ckf: szpt"])
    base_router = BaseCRUDRouter(
        "szpt-products", DicSzpt, SzptRepo, SzptDto, tags=["ckf: szpt"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/violations-count/{kkm_id}/{szpt_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_violations_count_by_kkm_id(
        kkm_id: int,
        szpt_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить количество нарушений по ККМ и СЗПТ"""
        response = await SzptRepo(session).get_violations_count_by_kkm_id(
            kkm_id, szpt_id
        )
        return response

    @sub_router.get("/last-violation-info/{kkm_id}/{szpt_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_last_violation_info(
        kkm_id: int,
        szpt_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить информацию о последнем нарушении"""
        response = await SzptRepo(session).get_last_receipt_with_violation(
            kkm_id, szpt_id
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация о нарушениях не найдена",
            )

        return response

    @sub_router.get(
        "/receipt-by-fiscal/{fiskal_sign}", response_model=LastCheckViolationDto
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipt_content_by_fiscal(
        fiskal_sign: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить содержимое чека по фискальному признаку"""
        payment_types = {0: "Оплата наличными", 1: "Карта", 4: "Мобильная оплата"}

        response = await SzptRepo(session).get_receipt_content(fiskal_sign)

        payment_type = payment_types.get(response["products"][0]["payment_type"])
        check_sum = round(
            sum(resp["full_item_price"] for resp in response["products"]), 2
        )
        nds_sum = sum(resp["item_nds"] for resp in response["products"])

        overcharge = 0
        price_per_unit = 0
        current_max_price = 0
        for resp in response["products"]:
            if resp["has_szpt_violation"] == True:
                overcharge += resp["price_per_unit"] - resp["current_max_price"]
                price_per_unit += resp["price_per_unit"]
                current_max_price += resp["current_max_price"]

        percent = round(
            ((price_per_unit - current_max_price) / current_max_price) * 100, 2
        )

        products = [
            ProductsViolationDto(
                item_name=prod["item_name"],
                full_item_price=prod["full_item_price"],
                max_price=prod["price"],
                price_per_unit=prod.get("price_per_unit"),
                has_szpt_violation=prod.get("has_szpt_violation", False),
                unit=prod.get("unit"),
            )
            for prod in response.get("products", [])
        ]

        return LastCheckViolationDto(
            products=products,
            payment_type=payment_type,
            check_sum=check_sum,
            nds_sum=nds_sum,
            percent=percent,
            overcharge=overcharge,
        )

    @sub_router.get("/by-year-regions")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipt_content(
        filters: Annotated[SzptRegionRequestDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await SzptRepo(session).count_by_year_and_regions(filters)

        return response

    @sub_router.get("/monthly/by-year-regions")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipt_content(
        filters: Annotated[SzptRegionRequestDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        response = await SzptRepo(session).monthly_by_year_and_region(filters)

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
