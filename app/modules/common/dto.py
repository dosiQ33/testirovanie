"""
Project: nam
Created Date: Monday February 3rd 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from typing import List, Optional
from fastapi import Query
from datetime import date
from pydantic import Field, BaseModel
from app.modules.common.utils import SerializedGeojson
from .enums import RegionEnum


class BasestDto(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class BaseDto(BasestDto):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    id: Optional[int] = Field()


class FindByIdNumberDto(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    id: int = Field()


class FindByIdStringDto(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    id: str = Field()


class FindByTextDto(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    text: str = Field()


class DtoWithShape(BaseDto):
    shape: SerializedGeojson

    # @field_validator("shape", mode="before")
    # def to_geojson(cls, value):
    #     return geojson_to_object(value)


class Bbox(BaseModel):
    class Config:
        from_attributes = True

    bbox: List[float] = Field(Query([]))
    srid: Optional[int] = Field(default=4326)


class TerritoryFilterDto(BasestDto):
    territory: Optional[str] = None


class ByYearAndRegionsFilterDto(TerritoryFilterDto):
    period_start: date
    period_end: date
    region: RegionEnum


class CountByTerritoryAndRegionsDto(TerritoryFilterDto):
    region: RegionEnum


class CountByYearAndRegionsDto(TerritoryFilterDto):
    year: int
    region: RegionEnum
    
    
class CountResponseDto(BasestDto):
    count: int
    
    
class ByMonthAndRegionsResponseDto(CountResponseDto):
    month: int

    

