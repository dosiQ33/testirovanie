from .dtos import (
    CountByRegionsDto,
    ByYearAndRegionsFilterDto, 
    ByMonthAndRegionsResponseDto,
    OrganizationsByYearAndRegionsResponseDto,
    PopulationMonthlyByYearAndRegionsResponseDto
)
from datetime import date
from typing import List

def to_regions_filter_dto(count_dto: CountByRegionsDto, is_current_year: bool) -> ByYearAndRegionsFilterDto:
    """мапим данные в фильтр для подсчета данных по регионам"""

    last_month = date.today().month if is_current_year else 12
    
    period_start = date(count_dto.year, 1, 1)
    period_end = date(count_dto.year, last_month, 1)
    
    return ByYearAndRegionsFilterDto(
        territory=count_dto.territory,
        period_start=period_start,
        period_end=period_end
    )

def to_organization_count_by_regions_response(rows: List[dict]) -> OrganizationsByYearAndRegionsResponseDto:
    """мапим найденные данные по организаторам в дто для передачи ответа"""
    
    monthly = [ByMonthAndRegionsResponseDto(**row) for row in rows]
    
    return OrganizationsByYearAndRegionsResponseDto(
        monthly=monthly,
        year_count=monthly[-1].count if monthly else 0
    )

def to_population_count_by_regions_response(rows: List[dict]) -> PopulationMonthlyByYearAndRegionsResponseDto:
    """мапим найденные данные по населению в дто для передачи ответа"""
    
    monthly = [ByMonthAndRegionsResponseDto(**row) for row in rows]
    
    return PopulationMonthlyByYearAndRegionsResponseDto(
        monthly=monthly
    )