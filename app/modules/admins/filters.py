from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import Employees, DicUl, DicRoles, DicFl


class DicUlFilter(Filter):
    id: Optional[int] = None
    ul_bin: Optional[str] = None
    ul_shortname: Optional[str] = None
    ul_name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicUl
        search_model_fields = ["ul_name", "ul_shortname"]


class DicRolesFilter(Filter):
    id: Optional[int] = None
    role_name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicRoles
        search_model_fields = ["role_name"]


class DicFlFilter(Filter):
    id: Optional[int] = None
    fl_iin: Optional[str] = None
    fl_surname: Optional[str] = None
    fl_name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicFl
        search_model_fields = ["fl_surname", "fl_name"]


class EmployeesFilter(Filter):
    id: Optional[int] = None
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role_id: Optional[int] = None
    login: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Employees
        search_model_fields = ["login"]
