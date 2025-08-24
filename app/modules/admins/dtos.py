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


# Create DTOs (обновленные - create_date заполняется автоматически)
class DicUlCreateDto(BasestDto):
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    # create_date заполняется автоматически в базе данных


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
    # create_date заполняется автоматически в базе данных


class EmployeesCreateDto(BasestDto):
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    # empl_create_date заполняется автоматически в базе данных
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None


# Update DTOs (новые)
class DicFlUpdateDto(BasestDto):
    iin: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class DicUlUpdateDto(BasestDto):
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None


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


# Filter DTOs (существующие с дополнениями)
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
    # Новые поля для фильтрации по дате
    empl_create_date_from: Optional[datetime] = None
    empl_create_date_to: Optional[datetime] = None

    # Дополнительные поля для фильтрации по связанным таблицам
    fl_surname: Optional[str] = None  # Фамилия из dic_fl
    fl_name: Optional[str] = None  # Имя из dic_fl
    fl_iin: Optional[str] = None  # ИИН из dic_fl
    ul_name: Optional[str] = None  # Название из dic_ul
    ul_bin: Optional[str] = None  # БИН из dic_ul
