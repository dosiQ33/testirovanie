from typing import Optional
from datetime import datetime
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import DicIndicators, Employees, DicUl, DicRoles, DicFl


class DicUlFilter(Filter):
    id: Optional[int] = None
    parent_id: Optional[int] = None
    bin: Optional[str] = None
    shortname: Optional[str] = None
    name: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None

    class Constants(Filter.Constants):
        model = DicUl
        search_model_fields = ["name", "shortname", "bin"]


class DicRolesFilter(Filter):
    id: Optional[int] = None
    role_name: Optional[str] = None
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
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None

    class Constants(Filter.Constants):
        model = DicFl
        search_model_fields = ["surname", "name", "iin"]


class EmployeesFilter(Filter):
    id: Optional[int] = None
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role: Optional[int] = None
    login: Optional[str] = None
    deleted: Optional[bool] = None
    blocked: Optional[bool] = None
    employee_position: Optional[str] = None
    employee_department: Optional[str] = None
    employee_status: Optional[str] = None

    empl_create_date__gte: Optional[datetime] = None
    empl_create_date__lte: Optional[datetime] = None

    fl: Optional[DicFlFilter] = FilterDepends(with_prefix("fl", DicFlFilter))
    ul: Optional[DicUlFilter] = FilterDepends(with_prefix("ul", DicUlFilter))
    role_ref: Optional[DicRolesFilter] = FilterDepends(
        with_prefix("role_ref", DicRolesFilter)
    )

    class Constants(Filter.Constants):
        model = Employees
        search_model_fields = ["login", "employee_position", "employee_department"]


class DicIndicatorsFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicIndicators
        search_model_fields = ["name"]
