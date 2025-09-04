from datetime import date, datetime
from typing import Optional

from app.modules.common.dto import BasestDto, DtoWithShape

class RoadsDto(DtoWithShape):
    code: str
    name: str
    parent_id: Optional[int]
    kato_code: Optional[str]
    type_id: int
    created_at: datetime
    updated_at: Optional[datetime]