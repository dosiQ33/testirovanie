from typing import Optional
from datetime import date, datetime
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import Employees, DicUl, DicRoles, DicFl


class DicUlFilter(Filter):
    id: Optional[int] = None
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    create_date: Optional[date] = None

    class Constants(Filter.Constants):
        model = DicUl
        search_model_fields = ["name", "shortname", "bin"]


class DicRolesFilter(Filter):
    id: Optional[int] = None
    role_name: Optional[str] = None
    actions: Optional[int] = None
    description: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicRoles
        search_model_fields = ["role_name"]


class DicFlFilter(Filter):
    id: Optional[int] = None
    iin: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    create_date: Optional[date] = None

    class Constants(Filter.Constants):
        model = DicFl
        search_model_fields = ["surname", "name", "iin"]


class EmployeesFilter(Filter):
    # Direct employee fields
    id: Optional[int] = None
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    empl_create_date: Optional[datetime] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None

    # Filtering by related entities
    fl: Optional[DicFlFilter] = FilterDepends(with_prefix("fl", DicFlFilter))
    ul: Optional[DicUlFilter] = FilterDepends(with_prefix("ul", DicUlFilter))
    role_ref: Optional[DicRolesFilter] = FilterDepends(
        with_prefix("role_ref", DicRolesFilter)
    )

    class Constants(Filter.Constants):
        model = Employees
        search_model_fields = ["login", "employee_position", "employee_department"]
