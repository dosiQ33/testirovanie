from typing import Annotated, List
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.database.deps import get_session_without_commit
from app.modules.common.router import request_key_builder, cache_ttl, BaseCRUDRouter
from app.modules.common.dto import Bbox
from .dtos import (
    KaztelecomHourDto,
    KaztelecomMobileDataDto,
    KaztelecomMobileDataFilterDto,
    KaztelecomStationsGeoDto,
    KaztelecomStationsGeoWithGeomDto,
    KaztelecomStationsGeoFilterDto,
    MobileDataAggregationDto,
    MobileDataByHourDto,
    MobileDataByDateDto,
)
from .models import KaztelecomHour, KaztelecomMobileData, KaztelecomStationsGeo
from .repository import (
    KaztelecomHourRepo,
    KaztelecomMobileDataRepo,
    KaztelecomStationsGeoRepo,
)

router = APIRouter(prefix="/mobile-data")


class KaztelecomHourRouter(APIRouter):
    sub_router = APIRouter(prefix="/hours", tags=["ext: kaztelecom-hours"])
    base_router = BaseCRUDRouter(
        "hours",
        KaztelecomHour,
        KaztelecomHourRepo,
        KaztelecomHourDto,
        tags=["ext: kaztelecom-hours"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class KaztelecomStationsGeoRouter(APIRouter):
    sub_router = APIRouter(prefix="/stations", tags=["ext: kaztelecom-stations"])
    base_router = BaseCRUDRouter(
        "stations",
        KaztelecomStationsGeo,
        KaztelecomStationsGeoRepo,
        KaztelecomStationsGeoDto,
        tags=["ext: kaztelecom-stations"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", summary="Фильтр станций по параметрам")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_stations(
        filters: Annotated[KaztelecomStationsGeoFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[KaztelecomStationsGeoDto]:
        """
        Фильтрация станций по различным параметрам:

        - **territory**: WKT геометрия для пространственной фильтрации
        - **region**: регион (частичное совпадение)
        - **city**: город (частичное совпадение)
        - **district**: район (частичное совпадение)
        - **oblast_id**: ID области
        - **raion_id**: ID района
        - **in_special_zone**: в специальной зоне (0/1)
        - **zone_type**: тип зоны
        """
        response = await KaztelecomStationsGeoRepo(session).filter_stations(filters)
        return [KaztelecomStationsGeoDto.model_validate(item) for item in response]

    @sub_router.get("/bbox", summary="Станции по bounding box")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_stations_by_bbox(
        bbox: Annotated[Bbox, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """
        Получить станции в указанном bounding box

        - **bbox**: массив координат [minx, miny, maxx, maxy]
        - **srid**: система координат (по умолчанию 4326)
        """
        response = await KaztelecomStationsGeoRepo(session).get_by_bbox(
            bbox.bbox, bbox.srid
        )
        return response

    @sub_router.get("/geom/{id}", summary="Станция с геометрией")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_station_with_geom(
        id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> KaztelecomStationsGeoWithGeomDto:
        """Получить станцию с геометрией по ID"""
        response = await KaztelecomStationsGeoRepo(session).get_one_by_id(id)
        return KaztelecomStationsGeoWithGeomDto.model_validate(response)


class KaztelecomMobileDataRouter(APIRouter):
    sub_router = APIRouter(prefix="/data", tags=["ext: kaztelecom-mobile-data"])
    base_router = BaseCRUDRouter(
        "data",
        KaztelecomMobileData,
        KaztelecomMobileDataRepo,
        KaztelecomMobileDataDto,
        tags=["ext: kaztelecom-mobile-data"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", summary="Фильтр мобильных данных")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_mobile_data(
        filters: Annotated[KaztelecomMobileDataFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[KaztelecomMobileDataDto]:
        """
        Фильтрация мобильных данных по параметрам:

        - **territory**: WKT геометрия для пространственной фильтрации
        - **date_from**: дата начала периода
        - **date_to**: дата окончания периода
        - **hour_id**: ID часа
        - **age_id**: ID возрастной группы
        - **income_id**: ID группы доходов
        - **gender_id**: ID пола
        - **region**: регион
        - **city**: город
        - **district**: район
        """
        response = await KaztelecomMobileDataRepo(session).filter_mobile_data(filters)
        return [KaztelecomMobileDataDto.model_validate(item) for item in response]

    @sub_router.get("/stats", summary="Агрегированная статистика")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_aggregation_stats(
        filters: Annotated[KaztelecomMobileDataFilterDto, Query()] = None,
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> MobileDataAggregationDto:
        """
        Получить агрегированную статистику по мобильным данным:

        - Общее количество записей
        - Суммарный трафик
        - Суммарные показатели max и out
        - Количество уникальных дат и часов
        """
        response = await KaztelecomMobileDataRepo(session).get_aggregation_stats(
            filters
        )
        return response

    @sub_router.get("/by-hour", summary="Группировка по часам")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_data_by_hour(
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[MobileDataByHourDto]:
        """
        Получить данные сгруппированные по часам:

        - Количество записей по каждому часу
        - Суммарный и средний трафик
        """
        response = await KaztelecomMobileDataRepo(session).get_data_by_hour()
        return [MobileDataByHourDto.model_validate(item) for item in response]

    @sub_router.get("/by-date", summary="Группировка по датам")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_data_by_date(
        limit: int = Query(30, ge=1, le=365, description="Количество дней (1-365)"),
        session: AsyncSession = Depends(get_session_without_commit),
    ) -> List[MobileDataByDateDto]:
        """
        Получить данные сгруппированные по датам:

        - **limit**: количество последних дней (по умолчанию 30)
        """
        response = await KaztelecomMobileDataRepo(session).get_data_by_date(limit)
        return [MobileDataByDateDto.model_validate(item) for item in response]


# Подключение всех роутеров
router.include_router(KaztelecomHourRouter())
router.include_router(KaztelecomStationsGeoRouter())
router.include_router(KaztelecomMobileDataRouter())
