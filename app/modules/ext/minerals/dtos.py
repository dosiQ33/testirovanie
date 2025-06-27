from typing import Optional

from pydantic import Field
from app.modules.common.dto import BasestDto
from app.modules.common.utils import SerializedGeojson


class MineralsLocContractsDto(BasestDto):
    id: int
    bin: Optional[str]
    name: Optional[str]
    locnumber: Optional[str]
    field_5: Optional[str]

    geom: SerializedGeojson


class MineralsLocContractsFilterDto(BasestDto):
    territory: Optional[str] = Field(
        None,
        description="Получить записи пересекающиеся с данной геометрией. Координаты в формате WKT SRID=4326",
        example="POLYGON((70.0 50.0, 70.0 60.0, 80.0 60.0, 80.0 50.0, 70.0 50.0))",
    )
