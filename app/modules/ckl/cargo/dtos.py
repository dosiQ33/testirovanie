from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.modules.common.dto import BaseDto, DtoWithShape, BasestDto
from app.modules.common.utils import SerializedGeojson

class CargosDto(BaseDto):
    customs_document_id: int
    description: str
    type_id: int
    weight_kg: float
    volume_m3: float
    net_weight: float
    gross_weight: float
    package_type_id: int
    temperature_mode: str
    is_dangerous: bool
    sender_id: int
    receiver_id: int
    tn_ved_id: int
    count: int