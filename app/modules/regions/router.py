from fastapi import APIRouter, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_without_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl
from app.modules.common.dto import CountByYearAndRegionsDto
from app.modules.common.mappers import to_regions_filter_dto
from .dtos import (
    PopulationCountByRegionDto,
    PopulationDto,
    PopulationByRegionsResponseDto,
    PopulationMonthlyByYearAndRegionsResponseDto,
    NalogPostuplenieDto, 
    TaxByRegionsResponseDto
)
from .repository import (
    PopulationRepo,
    NalogPostuplenieRepo
)
from .models import Populations, NalogPostuplenie  # noqa
from .mappers import to_population_count_by_regions_response, to_population_regions_filter_dto, to_population_count_by_regions_response
from datetime import date

router = APIRouter(prefix="/regions")


class PopulationsRouter(APIRouter):
    sub_router = APIRouter(prefix="/populations", tags=["regions: populations"])
    base_router = BaseCRUDRouter("populations", Populations, PopulationRepo, PopulationDto, tags=["regions: populations"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)
        
    @sub_router.get("/count/by-year-regions", response_model=PopulationByRegionsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  
    async def count_by_regions(
        count_dto: Annotated[PopulationCountByRegionDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
        repository = PopulationRepo(session)
        is_current_year = (count_dto.year == date.today().year)
        
        if is_current_year:
            MAX_DATES = [
                date(count_dto.year, 1, 1), date(count_dto.year, 4, 1),
                date(count_dto.year, 7, 1), date(count_dto.year, 10, 1)
            ]
                        
            population = await repository.get_current_year_maximum_by_region(
                count_dto=count_dto
            )
        
            gender_population = await repository.get_current_year_in_by_region(
                count_dto=count_dto, dates=MAX_DATES
            )
        else:
            POPULATION_DATE = date(count_dto.year, 12, 1)
            GENDER_DATE = date(count_dto.year, 10, 1)
            
            population = await repository.get_past_year_by_region(
                count_dto=count_dto, date_=POPULATION_DATE
            )
            
            gender_population = await repository.get_past_year_by_region(
                count_dto=count_dto, date_=GENDER_DATE
            )

        return PopulationByRegionsResponseDto(
            sum_people=population.people_num if population else 0,
            sum_male=gender_population.male_num if gender_population else 0,
            sum_female=gender_population.female_num if gender_population else 0
        )

    @sub_router.get("/count/monthly/by-year-regions", response_model=PopulationMonthlyByYearAndRegionsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  
    async def count_monthly_by_regions(
        count_dto: Annotated[PopulationCountByRegionDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):  
        is_current_year = (count_dto.year == date.today().year)
        filters = to_population_regions_filter_dto(
            count_dto=count_dto,
            is_current_year=is_current_year
        )
        
        rows = await PopulationRepo(session).get_population_monthly_by_region(filters=filters)
        
        return to_population_count_by_regions_response(rows=rows)
    
class NalogPostuplenieRouter(APIRouter):
    sub_router = APIRouter(prefix="/nalog-postuplenie", tags=["regions: nalog-postuplenie"])
    base_router = BaseCRUDRouter("nalog-postuplenie", NalogPostuplenie, NalogPostuplenieRepo, NalogPostuplenieDto, tags=["regions: nalog-postuplenie"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/tax/aggregated")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  
    async def get_tax_total_amount_by_regions(
        count_dto: Annotated[PopulationCountByRegionDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
        repository = NalogPostuplenieRepo(session)

        total_amount = await repository.get_total_amount_by_region(filters=count_dto)
        
        return total_amount

    @sub_router.get('/tax/monthly/by-region')
    @cache(expire=cache_ttl, key_builder=request_key_builder)  
    async def get_monthly_total_amount(
        count_dto: Annotated[PopulationCountByRegionDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
        is_current_year = (count_dto.year == date.today().year)
        filters = to_population_regions_filter_dto(
            count_dto=count_dto,
            is_current_year=is_current_year
        )

        rows = await NalogPostuplenieRepo(session).get_montly_total_by_region(filters=filters)

        return rows
    
router.include_router(PopulationsRouter())
router.include_router(NalogPostuplenieRouter())