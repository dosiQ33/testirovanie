"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from datetime import date
from typing import List, Optional


from app.modules.common.dto import BasestDto, ByMonthAndRegionsResponseDto

class PopulationDto(BasestDto):
    id: int
    oblast_id: Optional[int]
    raion_id: Optional[int]
    date_: Optional[date]

    people_num: Optional[int]
    male_num: Optional[int]
    female_num: Optional[int]


class PopulationByRegionsResponseDto(BasestDto):
    sum_people: int
    sum_male: int
    sum_female: int

class PopulationMonthlyByYearAndRegionsResponseDto(BasestDto):
    monthly: List[ByMonthAndRegionsResponseDto]