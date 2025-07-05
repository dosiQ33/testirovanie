from typing import Optional
from datetime import datetime, date
from app.modules.common.dto import BaseDto, BasestDto


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


class DicUlCreateDto(BasestDto):
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    create_date: Optional[date] = None


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
    create_date: Optional[date] = None


class EmployeesCreateDto(BasestDto):
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


class EmployeesFilterDto(BasestDto):
    """DTO for filtering employees"""

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
