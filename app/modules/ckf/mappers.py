from app.modules.common.dto import (
    ByMonthAndRegionsResponseDto
)
from .dtos import OrganizationsByYearAndRegionsResponseDto
from typing import List

def to_organization_count_by_regions_response(rows: List[dict]) -> OrganizationsByYearAndRegionsResponseDto:
    """мапим найденные данные по организаторам в дто для передачи ответа"""
    
    monthly = [ByMonthAndRegionsResponseDto(**row) for row in rows]
    
    return OrganizationsByYearAndRegionsResponseDto(
        monthly=monthly,
        year_count=monthly[-1].count if monthly else 0
    )