from typing import Optional
from datetime import date
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import (
    ExecFiles,
    Executions,
    Risks,
    DicRiskDegree,
    DicRiskType,
    DicRiskName,
    Orders,
    DicOrderStatus,
    DicOrderType,
)
from app.modules.ckf.models import Organizations


class DicRiskDegreeFilter(Filter):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicRiskDegree


class DicRiskTypeFilter(Filter):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicRiskType


class DicRiskNameFilter(Filter):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicRiskName


class OrganizationsFilter(Filter):
    iin_bin: Optional[str] = None

    class Constants(Filter.Constants):
        model = Organizations


class DicOrderStatusFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicOrderStatus


class DicOrderTypeFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = DicOrderType


class RisksFilter(Filter):
    id: Optional[int] = None
    risk_type: Optional[int] = None
    risk_name: Optional[int] = None
    risk_degree: Optional[int] = None
    organization_id: Optional[int] = None
    is_ordered: Optional[bool] = None

    risk_type_ref: Optional[DicRiskTypeFilter] = FilterDepends(
        with_prefix("risk_type_ref", DicRiskTypeFilter)
    )
    risk_name_ref: Optional[DicRiskNameFilter] = FilterDepends(
        with_prefix("risk_name_ref", DicRiskNameFilter)
    )
    risk_degree_ref: Optional[DicRiskDegreeFilter] = FilterDepends(
        with_prefix("risk_degree_ref", DicRiskDegreeFilter)
    )
    organization: Optional[OrganizationsFilter] = FilterDepends(
        with_prefix("organization", OrganizationsFilter)
    )

    class Constants(Filter.Constants):
        model = Risks


class OrdersFilter(Filter):
    id: Optional[int] = None
    order_date: Optional[date] = None
    order_deadline: Optional[date] = None
    order_num: Optional[int] = None
    employee_id: Optional[int] = None
    order_status: Optional[int] = None
    order_type: Optional[int] = None

    order_status_ref: Optional[DicOrderStatusFilter] = FilterDepends(
        with_prefix("order_status_ref", DicOrderStatusFilter)
    )
    order_type_ref: Optional[DicOrderTypeFilter] = FilterDepends(
        with_prefix("order_type_ref", DicOrderTypeFilter)
    )

    class Constants(Filter.Constants):
        model = Orders


class ExecutionsFilter(Filter):
    id: Optional[int] = None
    exec_date: Optional[date] = None
    order_id: Optional[int] = None
    exec_num: Optional[int] = None
    employee_id: Optional[int] = None
    is_accepted: Optional[bool] = None

    class Constants(Filter.Constants):
        model = Executions


class ExecFilesFilter(Filter):
    id: Optional[int] = None
    exec_id: Optional[int] = None
    name: Optional[str] = None
    file_name: Optional[str] = None
    ext: Optional[str] = None
    type: Optional[int] = None

    class Constants(Filter.Constants):
        model = ExecFiles
        search_model_fields = ["name", "file_name"]
