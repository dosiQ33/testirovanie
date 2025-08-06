from typing import List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import BaseExtRepository
from app.modules.common.utils import territory_to_geo_element
from .dtos import (
    KaztelecomMobileDataFilterDto,
    KaztelecomStationsGeoFilterDto,
    MobileDataAggregationDto,
)
from .models import KaztelecomHour, KaztelecomMobileData, KaztelecomStationsGeo


class KaztelecomHourRepo(BaseExtRepository):
    model = KaztelecomHour


class KaztelecomStationsGeoRepo(BaseExtRepository):
    model = KaztelecomStationsGeo

    async def filter_stations(self, filters: KaztelecomStationsGeoFilterDto):
        """Фильтрация станций по параметрам"""
        try:
            query = select(self.model)

            if filters.territory is not None:
                territory_geom = territory_to_geo_element(filters.territory)
                query = query.filter(
                    func.ST_Intersects(self.model.polygon_wkt, territory_geom)
                )

            if filters.region is not None:
                query = query.filter(self.model.region.ilike(f"%{filters.region}%"))

            if filters.city is not None:
                query = query.filter(self.model.city.ilike(f"%{filters.city}%"))

            if filters.district is not None:
                query = query.filter(self.model.district.ilike(f"%{filters.district}%"))

            if filters.oblast_id is not None:
                query = query.filter(self.model.oblast_id == filters.oblast_id)

            if filters.raion_id is not None:
                query = query.filter(self.model.raion_id == filters.raion_id)

            if filters.in_special_zone is not None:
                query = query.filter(
                    self.model.in_special_zone == filters.in_special_zone
                )

            if filters.zone_type is not None:
                query = query.filter(self.model.zone_type == filters.zone_type)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} станций по фильтрам.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при фильтрации станций: {e}")
            raise

    async def get_by_bbox(self, bbox: List[float], srid: int = 4326):
        """Получить станции по bounding box"""
        try:
            from sqlalchemy import text

            query = text(
                f"""
                SELECT id, region, city, district, lat_center, long_center, polygon_wkt
                FROM {self.model.__table__.schema}.{self.model.__tablename__}
                WHERE polygon_wkt && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, :srid)
                """
            ).bindparams(
                minx=bbox[0],
                miny=bbox[1],
                maxx=bbox[2],
                maxy=bbox[3],
                srid=srid,
            )

            result = await self._session.execute(query)
            records = result.fetchall()

            logger.info(f"Найдено {len(records)} станций в bounding box.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске станций по bbox: {e}")
            raise


class KaztelecomMobileDataRepo(BaseExtRepository):
    model = KaztelecomMobileData

    async def filter_mobile_data(self, filters: KaztelecomMobileDataFilterDto):
        """Фильтрация мобильных данных"""
        try:
            query = select(self.model)

            if filters.date_from is not None:
                query = query.filter(self.model.date >= filters.date_from)

            if filters.date_to is not None:
                query = query.filter(self.model.date <= filters.date_to)

            if filters.hour_id is not None:
                query = query.filter(self.model.hour_id == filters.hour_id)

            if filters.age_id is not None:
                query = query.filter(self.model.age_id == filters.age_id)

            if filters.income_id is not None:
                query = query.filter(self.model.income_id == filters.income_id)

            if filters.gender_id is not None:
                query = query.filter(self.model.gender_id == filters.gender_id)

            # Для территориальной фильтрации нужно присоединить таблицу станций
            if filters.territory is not None:
                territory_geom = territory_to_geo_element(filters.territory)
                query = query.join(
                    KaztelecomStationsGeo, self.model.zid_id == KaztelecomStationsGeo.id
                ).filter(
                    func.ST_Intersects(
                        KaztelecomStationsGeo.polygon_wkt, territory_geom
                    )
                )

            if filters.region is not None:
                query = query.join(
                    KaztelecomStationsGeo, self.model.zid_id == KaztelecomStationsGeo.id
                ).filter(KaztelecomStationsGeo.region.ilike(f"%{filters.region}%"))

            if filters.city is not None:
                query = query.join(
                    KaztelecomStationsGeo, self.model.zid_id == KaztelecomStationsGeo.id
                ).filter(KaztelecomStationsGeo.city.ilike(f"%{filters.city}%"))

            if filters.district is not None:
                query = query.join(
                    KaztelecomStationsGeo, self.model.zid_id == KaztelecomStationsGeo.id
                ).filter(KaztelecomStationsGeo.district.ilike(f"%{filters.district}%"))

            query = query.order_by(self.model.date.desc(), self.model.hour_id)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей мобильных данных.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при фильтрации мобильных данных: {e}")
            raise

    async def get_aggregation_stats(
        self, filters: KaztelecomMobileDataFilterDto = None
    ):
        """Получить агрегированную статистику"""
        try:
            query = select(
                func.count(self.model.id).label("total_records"),
                func.coalesce(func.sum(self.model.qnt_traf), 0).label("total_traffic"),
                func.coalesce(func.sum(self.model.qnt_max), 0).label("total_max"),
                func.coalesce(func.sum(self.model.qnt_out), 0).label("total_out"),
                func.count(func.distinct(self.model.date)).label("unique_dates"),
                func.count(func.distinct(self.model.hour_id)).label("unique_hours"),
            )

            # Применить фильтры если есть (упрощенная версия)
            if filters:
                if filters.date_from:
                    query = query.filter(self.model.date >= filters.date_from)
                if filters.date_to:
                    query = query.filter(self.model.date <= filters.date_to)
                if filters.hour_id:
                    query = query.filter(self.model.hour_id == filters.hour_id)

            result = await self._session.execute(query)
            row = result.one()

            return MobileDataAggregationDto(
                total_records=row.total_records,
                total_traffic=row.total_traffic,
                total_max=row.total_max,
                total_out=row.total_out,
                unique_dates=row.unique_dates,
                unique_hours=row.unique_hours,
            )

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении агрегированной статистики: {e}")
            raise

    async def get_data_by_hour(self):
        """Группировка данных по часам"""
        try:
            query = (
                select(
                    self.model.hour_id,
                    KaztelecomHour.hourly_cut,
                    func.count(self.model.id).label("total_records"),
                    func.coalesce(func.sum(self.model.qnt_traf), 0).label(
                        "total_traffic"
                    ),
                    func.coalesce(func.avg(self.model.qnt_traf), 0).label(
                        "avg_traffic"
                    ),
                )
                .join(KaztelecomHour, self.model.hour_id == KaztelecomHour.id)
                .group_by(self.model.hour_id, KaztelecomHour.hourly_cut)
                .order_by(self.model.hour_id)
            )

            result = await self._session.execute(query)
            rows = result.all()

            return [
                {
                    "hour_id": row.hour_id,
                    "hourly_cut": row.hourly_cut,
                    "total_records": row.total_records,
                    "total_traffic": row.total_traffic,
                    "avg_traffic": float(row.avg_traffic),
                }
                for row in rows
            ]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при группировке по часам: {e}")
            raise

    async def get_data_by_date(self, limit: int = 30):
        """Группировка данных по датам"""
        try:
            query = (
                select(
                    self.model.date,
                    func.count(self.model.id).label("total_records"),
                    func.coalesce(func.sum(self.model.qnt_traf), 0).label(
                        "total_traffic"
                    ),
                    func.count(func.distinct(self.model.hour_id)).label("unique_hours"),
                )
                .filter(self.model.date.is_not(None))
                .group_by(self.model.date)
                .order_by(self.model.date.desc())
                .limit(limit)
            )

            result = await self._session.execute(query)
            rows = result.all()

            return [
                {
                    "date": row.date,
                    "total_records": row.total_records,
                    "total_traffic": row.total_traffic,
                    "unique_hours": row.unique_hours,
                }
                for row in rows
            ]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при группировке по датам: {e}")
            raise
