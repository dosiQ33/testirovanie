from typing import List, Optional, Self
from datetime import datetime, date
from app.modules.common.dto import BasestDto
from pydantic import model_validator

from app.modules.auth.utils import get_password_hash


class TerritoryDto(BasestDto):
    id: int
    parent_id: Optional[int] = None
    type: Optional[str] = None
    name_ru: Optional[str] = None
    kato: Optional[str] = None
    parentkato: Optional[str] = None


class DicUlDto(BasestDto):
    id: int
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    create_date: Optional[date] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None

    oblast: Optional[TerritoryDto] = None
    raion: Optional[TerritoryDto] = None


class DicRolesDto(BasestDto):
    id: int
    role_name: Optional[str] = None
    actions: Optional[int] = None
    description: Optional[str] = None


class DicFlDto(BasestDto):
    id: int
    iin: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    create_date: Optional[date] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None


class DicIndicatorsDto(BasestDto):
    id: int
    name: Optional[str] = None


class EmployeeIndicatorDto(BasestDto):
    indicator_id: int
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[int] = None
    indicator: Optional[DicIndicatorsDto] = None


class EmployeesDto(BasestDto):
    id: int
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    empl_create_date: Optional[datetime] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None

    # Relationships
    fl: Optional[DicFlDto] = None
    ul: Optional[DicUlDto] = None
    role_ref: Optional[DicRolesDto] = None
    indicators: Optional[List[EmployeeIndicatorDto]] = None


class DicUlCreateDto(BasestDto):
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None


class DicRolesCreateDto(BasestDto):
    role_name: Optional[str] = None
    actions: Optional[int] = None
    description: Optional[str] = None


class DicFlCreateDto(BasestDto):
    iin: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None


class EmployeesCreateDto(BasestDto):
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None
    indicator_ids: Optional[List[int]] = None

    @model_validator(mode="after")
    def hash_password(self) -> Self:
        if self.password:
            self.password = get_password_hash(self.password)
        return self


class DicFlUpdateDto(BasestDto):
    iin: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None


class DicUlUpdateDto(BasestDto):
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None


class EmployeesUpdateDto(BasestDto):
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None
    indicator_ids: Optional[List[int]] = None

    @model_validator(mode="after")
    def hash_password(self) -> Self:
        if self.password:
            self.password = get_password_hash(self.password)
        return self


class EmployeesFilterDto(BasestDto):
    id: Optional[int] = None
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role_id: Optional[int] = None
    login: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None
    empl_create_date_from: Optional[datetime] = None
    empl_create_date_to: Optional[datetime] = None

    fl_surname: Optional[str] = None
    fl_name: Optional[str] = None
    fl_iin: Optional[str] = None
    ul_name: Optional[str] = None
    ul_bin: Optional[str] = None


class EmployeeLoginDto(BasestDto):
    login: Optional[str] = None
    password: Optional[str] = None


class EmployeeInfoDto(BasestDto):
    id: int
    login: str
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None
    deleted: bool
    blocked: bool

    fl: Optional[DicFlDto] = None
    ul: Optional[DicUlDto] = None
    role_ref: Optional[DicRolesDto] = None
