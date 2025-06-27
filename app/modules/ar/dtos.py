"""
Project: nam
Created Date: Monday February 3rd 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from __future__ import annotations
from typing import Dict, List, Optional

from app.modules.common.dto import BaseDto, BasestDto
from app.modules.common.utils import SerializedGeojson


class BaseDDto(BaseDto):
    code: int
    value_kz: str
    value_ru: str
    short_value_kz: Optional[str] = None
    short_value_ru: Optional[str] = None
    actual: bool


class DAtsTypesDto(BaseDDto):
    pass


class DGeonimsTypesDto(BaseDDto):
    this_is: Optional[str] = None


class DBuildingsPointersDto(BaseDDto):
    pass


class DRoomsTypesDto(BaseDDto):
    pass


class SAtsDto(BaseDto):
    parent_id: Optional[int]
    # parent: Optional[SAtsDto]

    name_kz: str
    name_ru: str
    rco: Optional[str]
    cato: Optional[str]

    d_ats_type_id: Optional[int]
    d_ats_type: Optional[DAtsTypesDto] = None

    actual: bool

    full_address_ru: Optional[str]
    full_address_kz: Optional[str]

    path: Optional[List[Dict]]
    is_leaf: bool

    shape: SerializedGeojson


class SGeonimsDto(BaseDto):
    parent_id: Optional[int]
    # parent: Optional[Any] = None

    name_kz: str
    name_ru: str
    rco: Optional[str]
    cato: Optional[str]

    s_ats_id: Optional[int]
    s_ats: Optional[SAtsDto] = None

    d_geonims_type_id: Optional[int]
    d_geonims_type: Optional[DGeonimsTypesDto] = None

    actual: bool

    full_address_ru: Optional[str]
    full_address_kz: Optional[str]

    path: Optional[List[Dict]]
    is_leaf: bool

    shape: SerializedGeojson


class SGroundsDto(BaseDto):
    s_ats_id: Optional[int]
    s_ats: Optional[SAtsDto] = None

    s_geonim_id: Optional[int]
    s_geonim: Optional[SGeonimsDto] = None

    rca: Optional[str]
    number: Optional[str]
    cadastre_number: Optional[str]

    actual: bool

    shape: SerializedGeojson


class SBuildingsDto(BaseDto):
    parent_id: Optional[int]
    # parent: Optional[Any] = None

    name_kz: Optional[str]
    name_ru: Optional[str]

    s_ats_id: Optional[int]
    s_ats: Optional[SAtsDto] = None

    s_geonim_id: Optional[int]
    s_geonim: Optional[SGeonimsDto] = None

    d_buildings_pointer_id: Optional[int]
    d_buildings_pointer: Optional[DBuildingsPointersDto] = None

    rca: Optional[str] = None
    number: Optional[str] = None
    distance: Optional[float] = None
    this_is: Optional[str] = None

    actual: bool

    full_address_ru: Optional[str] = None
    full_address_kz: Optional[str] = None

    path: Optional[List[Dict]]

    shape: SerializedGeojson


class SPbDto(BaseDto):
    s_building_id: Optional[int]
    s_building: Optional[SBuildingsDto] = None

    d_room_type_id: Optional[int]
    d_room_type: Optional[DRoomsTypesDto] = None

    rca: Optional[str] = None
    number: Optional[str] = None

    actual: bool

    full_address_ru: Optional[str] = None
    full_address_kz: Optional[str] = None


class AddBuildingCoordsDto(BasestDto):
    region: Optional[str] = None
    district: Optional[str] = None
    locality: Optional[str] = None
    locality_district: Optional[str] = None
    street: Optional[str] = None
    building_number: str

    lat: float
    lon: float
