from fastapi import APIRouter, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_without_commit
from app.modules.common.dto import CountByYearAndRegionsDto
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl
from app.modules.common.mappers import to_regions_filter_dto
from .dtos import (
    PopulationDto,
    PopulationByRegionsResponseDto,
    PopulationMonthlyByYearAndRegionsResponseDto
)
from .repository import (
    PopulationRepo
)
from .models import Populations  # noqa
from .mappers import to_population_count_by_regions_response
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
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):
        repository = PopulationRepo(session)
        is_current_year = (count_dto.year == date.today().year)
        
        if is_current_year:
            MAX_DATES = [
                date(count_dto.year, 1, 1), date(count_dto.year, 4, 1),
                date(count_dto.year, 7, 1), date(count_dto.year, 10, 1)
            ]
                        
            populations = await repository.get_many_current_year_maximum_by_region(
                count_dto=count_dto
            )
        
            gender_populations = await repository.get_many_current_year_in_by_region(
                count_dto=count_dto, dates=MAX_DATES
            )
        else:
            POPULATION_DATE = date(count_dto.year, 12, 1)
            GENDER_DATE = date(count_dto.year, 10, 1)
            
            populations = await repository.get_many_past_year_by_region(
                count_dto=count_dto, date_=POPULATION_DATE
            )
            
            gender_populations = await repository.get_many_past_year_by_region(
                count_dto=count_dto, date_=GENDER_DATE
            )
        
        sum_people = sum(population.people_num for population in populations if population.people_num)
        sum_male = sum(population.male_num for population in gender_populations if population.male_num)
        sum_female = sum(population.female_num for population in gender_populations if population.female_num)
        
        return PopulationByRegionsResponseDto(
            sum_people=sum_people,
            sum_male=sum_male,
            sum_female=sum_female
        )

    @sub_router.get("/count/monthly/by-year-regions", response_model=PopulationMonthlyByYearAndRegionsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)  
    async def count_monthly_by_regions(
        count_dto: Annotated[CountByYearAndRegionsDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit)
    ):  
        is_current_year = (count_dto.year == date.today().year)
        filters = to_regions_filter_dto(count_dto=count_dto, is_current_year=is_current_year)
        
        rows = await PopulationRepo(session).get_population_monthly_by_region(filters=filters)
        
        return to_population_count_by_regions_response(rows=rows)
    
router.include_router(PopulationsRouter())