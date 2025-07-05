from sqlalchemy import func, select, text, cast, Integer
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.dto import ByYearAndRegionsFilterDto, CountByYearAndRegionsDto
from app.modules.common.enums import RegionEnum
from app.modules.common.repository import BaseRepository
from app.modules.common.utils import territory_to_geo_element
from app.modules.ext.kazgeodesy.models import KazgeodesyRkOblasti, KazgeodesyRkRaiony #осторожно
from .models import (
    Populations
)
from typing import List
from datetime import date

class PopulationRepo(BaseRepository):
    model = Populations
    
    def apply_region_join(self, query, region: RegionEnum, territory: str):
        
        territory_geom = territory_to_geo_element(territory=territory, srid=4326)
        
        if region == RegionEnum.oblast:
            query = (
                query.join(
                    KazgeodesyRkOblasti,
                    Populations.oblast_id == KazgeodesyRkOblasti.id
                ).filter(func.ST_Intersects(KazgeodesyRkOblasti.geom, territory_geom))
            )
        elif region == RegionEnum.raion:
            query = (
                query.join(
                    KazgeodesyRkRaiony,
                    Populations.raion_id == KazgeodesyRkRaiony.id
                ).filter(func.ST_Intersects(KazgeodesyRkRaiony.geom, territory_geom))
            )
        
        return query
    
    async def get_population_monthly_by_region(self, filters: ByYearAndRegionsFilterDto):
        try:
            
            month_series = select(
                func.generate_series(
                    filters.period_start,
                    filters.period_end,
                    text("interval '1 month'")
                ).label("month_start")
            ).cte("month_series")

            month_col = month_series.c.month_start
            month_start = func.date_trunc("month", month_col)

            query = (
                select(
                    cast(func.extract("month", month_start), Integer).label("month"),
                    func.count().label("count")
                )
                .select_from(
                    month_series
                    .join(
                        Populations,
                        Populations.date_ == month_start
                    )
                )
                .group_by(month_start)
                .order_by(month_start)
            )
            
            query = self.apply_region_join(query=query, region=filters.region, territory=filters.territory)
            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "count": row.count} for row in rows]
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise
        
    async def get_many_past_year_by_region(self, count_dto: CountByYearAndRegionsDto, date_: date):
        try:
            query = select(Populations).filter(Populations.date_ == date_)
            query = self.apply_region_join(query=query, region=count_dto.region, territory=count_dto.territory)
            
            result = await self._session.execute(query)
            records = result.scalars().all()
            
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_many_current_year_maximum_by_region(self, count_dto: CountByYearAndRegionsDto):
        try:
            max_date_subq = (
                select(func.max(Populations.date_))
                .where(
                    Populations.date_ >= date(count_dto.year, 1, 1),
                    Populations.date_ <= date(count_dto.year, 12, 31)
                )
                .scalar_subquery()
            )
            
            query = select(Populations).where(Populations.date_ == max_date_subq)
            
            query = self.apply_region_join(query=query, region=count_dto.region, territory=count_dto.territory)

            result = await self._session.execute(query)
            records = result.scalars().all()
            
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_many_current_year_in_by_region(self, count_dto: CountByYearAndRegionsDto, dates: List[date]):
        try:
            max_qdate_subq = (
                select(func.max(Populations.date_))
                .where(Populations.date_.in_(dates))
                .scalar_subquery()
            )
            
            query = select(Populations).where(Populations.date_ == max_qdate_subq)
            
            query = self.apply_region_join(query=query, region=count_dto.region, territory=count_dto.territory)

            result = await self._session.execute(query)
            records = result.scalars().all()
            
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise