from typing import Optional

from app.modules.common.dto import (
    BasestDto,
    DtoWithShape
)

class IucAlkoDto(BasestDto):
    id: int

    iin_bin: str
    name_ru: str
    name_kz: str
    region: str 
    district: str
    status: str
    status_elicense: str
    arc_code: Optional[str]

    organization_id: Optional[int]

class IucNeftebasaCoordinatesTempDto(DtoWithShape):
    id: int

    iin_bin: str
    subject_name: str
    object_name: str
    object_type: str
    region: str
    district: str
    address: str
    arc_code: Optional[str]
    status: str
    status_in_oiltrack: str
    street_unique: str
    found_address: str

    organization_id: Optional[int]


class IucAzsCoordinatesTempDto(DtoWithShape):
    id: int

    iin_bin: str
    subject_name: str
    object_name: str
    production_type: str
    region: str
    district: str
    address: str
    arc_code: Optional[str]
    status: str
    street_unique: str
    found_address: str

    organization_id: Optional[int]


class IucNpzCoordinatesTempDto(DtoWithShape):
    id: int

    iin_bin: str
    subject_name: str
    object_name: str
    object_type: str
    region: str
    district: str
    address: str
    arc_code: str
    status: str
    street_unique: str
    found_address: str

    organization_id: Optional[int]


class IucZernoCoordinatesTempDto(DtoWithShape):
    id: int

    iin_bin: str
    subject_name: str
    region: str
    district: str
    address: str
    status: str
    granary_capacity_tons: str
    load_capacity_tons: str
    arc_code: Optional[str]
    street_unique: str
    coordinates: str
    found_address: str

    organization_id: Optional[int]

class IucAlkoResponseDto(BasestDto):
    name_ru: str
    iin_bin: str
    address: str
    organization_id: Optional[int]

class IucZernoResponseDto(BasestDto):
    subject_name: str
    iin_bin: str
    address: str
    granary_capacity_tons: str
    load_capacity_tons: str
    organization_id: Optional[int]

class IucNeftebasaResponseDto(BasestDto):
    object_name: str
    iin_bin: str
    address: str
    organization_id: Optional[int]

class IucNpzResponseDto(BasestDto):
    object_name: str
    iin_bin: str
    address: str
    organization_id: Optional[int]

class IucAzsResponseDto(BasestDto):
    object_name: str
    iin_bin: str
    address: str
    organization_id: Optional[int]