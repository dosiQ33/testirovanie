from typing import Optional
from app.modules.common.dto import BasestDto


class OkedsDto(BasestDto):
    id: int
    code: Optional[str]
    name_ru: Optional[str]
    name_kz: Optional[str]
