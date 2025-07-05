from fastapi_filter import FilterDepends, with_prefix
from app.modules.ckf.models import Organizations, RiskInfos
from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter

from app.modules.nsi.models import OkedsOld, RiskDegrees


class RiskDegreesFilter(Filter):
    id: Optional[int] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = RiskDegrees


class RiskInfoFilter(Filter):
    id: Optional[int] = None
    risk_degree: Optional[RiskDegreesFilter] = FilterDepends(with_prefix("risk_degree", RiskDegreesFilter))

    class Constants(Filter.Constants):
        model = RiskInfos


class OkedsFilter(Filter):
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None

    class Constants(Filter.Constants):
        model = OkedsOld


class OrganizationsFilter(Filter):
    id: Optional[int] = None
    id__in: Optional[list[int]] = None

    iin_bin: Optional[str] = None
    name_ru: Optional[str] = None
    name_kk: Optional[str] = None

    risk_info: Optional[RiskInfoFilter] = FilterDepends(with_prefix("risk_info", RiskInfoFilter))
    oked: Optional[OkedsFilter] = FilterDepends(with_prefix("oked", OkedsFilter))

    class Constants(Filter.Constants):
        model = Organizations
