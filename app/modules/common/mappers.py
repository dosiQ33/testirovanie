from .dto import (
    CountByYearAndRegionsDto,
    ByYearAndRegionsFilterDto,
)
from datetime import date

def to_regions_filter_dto(count_dto: CountByYearAndRegionsDto, is_current_year: bool) -> ByYearAndRegionsFilterDto:
    """мапим данные в фильтр для подсчета данных по регионам"""

    last_month = date.today().month if is_current_year else 12
    
    period_start = date(count_dto.year, 1, 1)
    period_end = date(count_dto.year, last_month, 1)
    
    return ByYearAndRegionsFilterDto(
        territory=count_dto.territory,
        period_start=period_start,
        period_end=period_end,
        region=count_dto.region
    )