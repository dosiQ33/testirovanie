from typing import List
from datetime import date

from app.modules.common.dto import (
    ByMonthAndRegionsResponseDto,
)
from .dtos import PopulationCountByRegionDto, PopulationPeriodFilterDto, PopulationMonthlyByYearAndRegionsResponseDto

def to_population_count_by_regions_response(rows: List[dict]) -> PopulationMonthlyByYearAndRegionsResponseDto:
    """мапим найденные данные по населению в дто для передачи ответа"""
    
    monthly = [ByMonthAndRegionsResponseDto(**row) for row in rows]
    
    return PopulationMonthlyByYearAndRegionsResponseDto(
        monthly=monthly
    )
    
def to_population_regions_filter_dto(count_dto: PopulationCountByRegionDto, is_current_year: bool) -> PopulationPeriodFilterDto:
    """мапим данные в фильтр для подсчета данных по регионам"""

    last_month = date.today().month if is_current_year else 12
    
    return PopulationPeriodFilterDto(
        region_id=count_dto.region_id,
        period_start=date(count_dto.year, 1, 1),
        period_end=date(count_dto.year, last_month, 1),
        year=count_dto.year,
        region=count_dto.region
    )