from sqlalchemy import func, select, text, cast, Integer, literal, or_, union
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.enums import RegionEnum
from app.modules.common.repository import BaseRepository
from app.modules.common.dto import ByYearAndRegionsFilterDto
from app.modules.common.utils import territory_to_geo_element
from app.modules.nsi.models import Ugds
from app.modules.ext.kazgeodesy.models import KazgeodesyRkOblasti, KazgeodesyRkRaiony #осторожно
from .models import (
    Populations,
    NalogPostuplenie
)
from .dtos import (
    PopulationCountByRegionDto,
    PopulationPeriodFilterDto,
)
from typing import List
from datetime import date

class PopulationRepo(BaseRepository):
    model = Populations
    
    def apply_region_filter(self, query, region: RegionEnum, region_id: int):        
        if region == RegionEnum.oblast or region == RegionEnum.rk:
            query = (
                query.filter(Populations.oblast_id == region_id)
            )
        elif region == RegionEnum.raion:
            query = (
                query.filter(Populations.raion_id == region_id)
            )
        
        return query
    
    async def get_population_monthly_by_region(self, filters: PopulationPeriodFilterDto):
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
                    func.coalesce(Populations.people_num, 0).label("count")
                )
                .select_from(
                    month_series
                    .join(
                        Populations,
                        Populations.date_ == month_start
                    )
                )
                .order_by(month_start)
            )

            query = self.apply_region_filter(query=query, region=filters.region, region_id=filters.region_id)
            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "count": row.count} for row in rows]
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise
        
    async def get_past_year_by_region(self, count_dto: PopulationCountByRegionDto, date_: date):
        try:
            query = select(Populations).filter(Populations.date_ == date_)
            
            query = self.apply_region_filter(query=query, region=count_dto.region, region_id=count_dto.region_id)
            
            result = await self._session.execute(query)
            record = result.scalars().all()
            
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_current_year_maximum_by_region(self, count_dto: PopulationCountByRegionDto):
        try:
            max_date_subq = (
                select(func.max(Populations.date_))
                .where(
                    Populations.date_ >= date(count_dto.year, 1, 1),
                    Populations.date_ <= date(count_dto.year, 12, 31)
                )
            )
            max_date_subq = self.apply_region_filter(query=max_date_subq, region=count_dto.region, region_id=count_dto.region_id)
            max_date_subq = max_date_subq.scalar_subquery()
            
            query = select(Populations).filter(Populations.date_ == max_date_subq)
            
            query = self.apply_region_filter(query=query, region=count_dto.region, region_id=count_dto.region_id)

            result = await self._session.execute(query)
            record = result.scalars().first() # на случай если есть дубли
            
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_current_year_in_by_region(self, count_dto: PopulationCountByRegionDto, dates: List[date]):
        try:
            max_qdate_subq = (
                select(func.max(Populations.date_))
                .where(Populations.date_.in_(dates))
                .scalar_subquery()
            )
            
            query = select(Populations).where(Populations.date_ == max_qdate_subq)
            
            query = self.apply_region_filter(query=query, region=count_dto.region, region_id=count_dto.region_id)

            result = await self._session.execute(query)
            record = result.scalars().first() # на случай дублей
            
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

class NalogPostuplenieRepo(BaseRepository):
    model = NalogPostuplenie

    def apply_region_and_ugds_subquery(self, query, region: RegionEnum, region_id: int):        
        if region == RegionEnum.oblast or region == RegionEnum.rk:
            ugd_ids_main = select(Ugds.id).where(Ugds.oblast_id == region_id)

            ugd_ids_children = select(Ugds.id).where(
                Ugds.parent_id.in_(
                    select(Ugds.id).where(Ugds.oblast_id == region_id)
                )
            )

            all_ugd_ids = union(ugd_ids_main, ugd_ids_children).subquery()
            query = query.filter(NalogPostuplenie.ugd_id.in_(select(all_ugd_ids.c.id)))
            
        elif region == RegionEnum.raion:
            ugd_ids_subq = select(Ugds.id).where(Ugds.raion_id == region_id).subquery()

            query = query.filter(NalogPostuplenie.ugd_id.in_(select(ugd_ids_subq.c.id)))

        
        return query

    async def get_total_amount_by_region(self, filters: PopulationCountByRegionDto):
        try:
            query = (
                select(
                    func.coalesce(func.sum(NalogPostuplenie.total_amount), 0).label("total_sum")
                )
                .filter(
                    NalogPostuplenie.rb == True,
                    NalogPostuplenie.month >= date(filters.year, 1, 1),
                    NalogPostuplenie.month <= date(filters.year, 12, 31)
                )
            )

            query = self.apply_region_and_ugds_subquery(query=query, region=filters.region, region_id=filters.region_id)
            result = await self._session.execute(query)
            row = result.one()

            return {"total_sum": float(row.total_sum)}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы налогов по региону: {e}")
            raise

    async def get_montly_total_by_region(self, filters: PopulationPeriodFilterDto):
        try:
            month_extract = func.extract("month", NalogPostuplenie.month)

            query = (
                select(
                    cast(month_extract, Integer).label("month"),
                    func.coalesce(func.sum(NalogPostuplenie.total_amount), 0).label("total_sum")
                )
                .filter(
                    NalogPostuplenie.rb == True,
                    NalogPostuplenie.month >= date(filters.year, 1, 1),
                    NalogPostuplenie.month <= date(filters.year, 12, 31)
                )
                .group_by(month_extract)
                .order_by(month_extract)
            )

            query = self.apply_region_and_ugds_subquery(query=query, region=filters.region, region_id=filters.region_id)
            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "total_sum": row.total_sum} for row in rows]
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы налогов по региону: {e}")
            raise