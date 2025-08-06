from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import Field

from app.modules.common.dto import BasestDto
from app.modules.common.utils import SerializedGeojson


class KaztelecomHourDto(BasestDto):
    id: int
    hourly_cut: Optional[str] = None


class KaztelecomStationsGeoDto(BasestDto):
    id: int
    diag_size: Optional[Decimal] = None

    # Coordinates
    lat_bot_left: Optional[Decimal] = None
    long_bot_left: Optional[Decimal] = None
    lat_bot_right: Optional[Decimal] = None
    long_bot_right: Optional[Decimal] = None
    lat_top_right: Optional[Decimal] = None
    long_top_right: Optional[Decimal] = None
    lat_top_left: Optional[Decimal] = None
    long_top_left: Optional[Decimal] = None
    lat_center: Optional[Decimal] = None
    long_center: Optional[Decimal] = None

    # Location info
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

    # Foreign keys
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None

    # Zone info
    in_special_zone: Optional[int] = None
    zone_id: Optional[int] = None
    zone_type: Optional[int] = None


class KaztelecomStationsGeoWithGeomDto(KaztelecomStationsGeoDto):
    """DTO с геометрией для отдельного эндпоинта"""

    polygon_wkt: Optional[SerializedGeojson] = None


class KaztelecomMobileDataDto(BasestDto):
    id: int
    date: Optional[date] = None
    hour_id: Optional[int] = None
    zid_id: Optional[int] = None
    age_id: Optional[int] = None
    income_id: Optional[int] = None
    gender_id: Optional[int] = None
    zid_home: Optional[int] = None
    zid_work: Optional[int] = None
    qnt_max: Optional[int] = None
    qnt_traf: Optional[int] = None
    qnt_out: Optional[int] = None

    # Relationship
    hour: Optional[KaztelecomHourDto] = None


class KaztelecomMobileDataFilterDto(BasestDto):
    """DTO для фильтрации мобильных данных"""

    territory: Optional[str] = Field(
        None,
        description="Получить записи пересекающиеся с данной геометрией. Координаты в формате WKT SRID=4326",
        example="POLYGON((70.0 50.0, 70.0 60.0, 80.0 60.0, 80.0 50.0, 70.0 50.0))",
    )
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    hour_id: Optional[int] = None
    age_id: Optional[int] = None
    income_id: Optional[int] = None
    gender_id: Optional[int] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None


class KaztelecomStationsGeoFilterDto(BasestDto):
    """DTO для фильтрации станций"""

    territory: Optional[str] = Field(
        None,
        description="Получить записи пересекающиеся с данной геометрией. Координаты в формате WKT SRID=4326",
        example="POLYGON((70.0 50.0, 70.0 60.0, 80.0 60.0, 80.0 50.0, 70.0 50.0))",
    )
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
    in_special_zone: Optional[int] = None
    zone_type: Optional[int] = None


class MobileDataAggregationDto(BasestDto):
    """DTO для агрегированной статистики"""

    total_records: int
    total_traffic: int
    total_max: int
    total_out: int
    unique_dates: int
    unique_hours: int


class MobileDataByHourDto(BasestDto):
    """DTO для группировки по часам"""

    hour_id: int
    hourly_cut: Optional[str] = None
    total_records: int
    total_traffic: int
    avg_traffic: float


class MobileDataByDateDto(BasestDto):
    """DTO для группировки по датам"""

    date: date
    total_records: int
    total_traffic: int
    unique_hours: int
