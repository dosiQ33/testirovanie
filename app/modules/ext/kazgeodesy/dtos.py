from typing import Optional
from app.modules.common.dto import BasestDto
from app.modules.common.utils import SerializedGeojson


class KazgeodesyRkDto(BasestDto):
    id: int
    parent_id: Optional[int]

    type: Optional[str]

    name_ru: Optional[str]

    kato: Optional[str]
    parentkato: Optional[str]

    # geom: SerializedGeojson


class KazgeodesyRkWithGeomDto(BasestDto):
    id: int
    parent_id: Optional[int]

    type: Optional[str]

    name_ru: Optional[str]

    kato: Optional[str]
    parentkato: Optional[str]

    geom: SerializedGeojson
