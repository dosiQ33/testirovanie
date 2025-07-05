from typing import List

from app.modules.common.dto import (
    ByMonthAndRegionsResponseDto
)
from .dtos import PopulationMonthlyByYearAndRegionsResponseDto

def to_population_count_by_regions_response(rows: List[dict]) -> PopulationMonthlyByYearAndRegionsResponseDto:
    """мапим найденные данные по населению в дто для передачи ответа"""
    
    monthly = [ByMonthAndRegionsResponseDto(**row) for row in rows]
    
    return PopulationMonthlyByYearAndRegionsResponseDto(
        monthly=monthly
    )