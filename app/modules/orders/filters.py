from typing import Optional
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import Risks, DicRiskDegree, DicRiskType, DicRiskName
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


class RisksFilter(Filter):
    id: Optional[int] = None
    risk_type: Optional[int] = None
    risk_name: Optional[int] = None
    risk_degree: Optional[int] = None
    organization_id: Optional[int] = None

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
