"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import status, HTTPException
from sqlalchemy import distinct, func, select, text, or_, cast, Integer, and_, union_all, literal, case
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from collections import defaultdict

from app.modules.common.dto import Bbox, ByYearAndRegionsFilterDto, CountByTerritoryAndRegionsDto, CountByYearAndRegionsDto
from app.modules.common.repository import BaseRepository, BaseWithKkmRepository, BaseWithOrganizationRepository
from app.modules.common.utils import wkb_to_geojson, territory_to_geo_element
from app.modules.common.models import BaseModel
from app.modules.common.enums import RegionEnum
from .dtos import KkmsFilterDto, OrganizationsFilterDto
from .models import (
    EsfBuyer,
    EsfBuyerDaily,
    EsfBuyerMonth,
    EsfSeller,
    EsfSellerDaily,
    EsfSellerMonth,
    Fno,
    FnoTypes,
    Organizations,
    Kkms,
    Receipts,
    ReceiptsAnnual,
    ReceiptsDaily,
    RiskInfos
)
from typing import Optional
from datetime import date

class OrganizationsRepo(BaseRepository):
    model = Organizations

    async def get_by_bbox(self, dto: Bbox):
        # 71.389166,51.117415,71.390796,51.118253

        try:
            query = text(
                f"SELECT id, iin_bin, name_ru, shape FROM {self.model.__tablename__} WHERE shape && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, :srid);"
            ).bindparams(minx=dto.bbox[0], miny=dto.bbox[1], maxx=dto.bbox[2], maxy=dto.bbox[3], srid=dto.srid)

            result = await self._session.execute(query)

            records = result.fetchall()

            logger.info(f"Найдено {len(records)} записей.")

            objects = []
            for record in records:
                obj = {
                    "id": record[0],
                    "iin_bin": record[1],
                    "name_ru": record[2],
                    "shape": wkb_to_geojson(record[3]),
                }
                objects.append(obj)

            return objects
        except SQLAlchemyError as e:
            logger.error(e)
            logger.error(f"Ошибка при поиске записей по bbox {dto}: {e}")
            raise

    async def get_kkms(self, id: int):
        org = await self.get_one_by_id(id)

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организация не найдена")

        return org.kkms

    async def get_branches(self, bin_root: str):
        try:
            query = select(self.model).filter(Organizations.bin_root == bin_root)
            result = await self._session.execute(query)
            orgs = result.unique().scalars().all()

            logger.info(f"Найдено {len(orgs)} филиалов для корневого БИН {bin_root}.")

            # If no records found return empty list
            if not orgs:
                return []

            return orgs
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске филиалов по корневому БИН {bin_root}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при поиске филиалов")

    async def filter(self, filters: OrganizationsFilterDto):
        try:
            query = select(self.model)

            if filters.territory is not None:
                query = query.filter(Organizations.shape.ST_Intersects("SRID=4326;" + filters.territory))

            if filters.iin_bin is not None:
                query = query.filter(Organizations.iin_bin == filters.iin_bin)

            if filters.oked_ids is not None:
                query = query.filter(Organizations.oked_id.in_(filters.oked_ids))

            if filters.risk_degree_ids is not None:
                query = query.join(RiskInfos).filter(RiskInfos.risk_degree_id.in_(filters.risk_degree_ids))

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей.")

            # If no records found return empty list
            if not records:
                return []

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise
    
    async def count_monthly_by_year_and_regions(self, filters: ByYearAndRegionsFilterDto):
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
            month_end = month_start + text("interval '1 month'") - text("interval '1 day'")
            
            conditions = [
                Organizations.date_start <= month_end,
                or_(
                    Organizations.date_stop.is_(None),
                    Organizations.date_stop > month_end
                )
            ]
            
            if filters.region != RegionEnum.rk: 
                territory_geom = territory_to_geo_element(territory=filters.territory, srid=4326)
                conditions.append(func.ST_Intersects(Organizations.shape, territory_geom))
            
            join_on = and_(*conditions)
            query = (
                select(
                    cast(func.extract("month", month_start), Integer).label("month"),
                    func.count().label("count")
                )
                .select_from(month_series.join(Organizations, join_on))
                .group_by(month_start)
                .order_by(month_start)
            )

            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "count": row.count} for row in rows]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise

    async def count_by_year_and_regions(self, count_dto: CountByYearAndRegionsDto, date_: Optional[date]):
        try:
            query = select(func.count()).select_from(Organizations)
            
            if date_:
                query = query.filter(
                    Organizations.date_start <= date_,
                    or_(
                        Organizations.date_stop.is_(None),
                        Organizations.date_stop > date_
                    )
                )
            else:
                query = query.filter(Organizations.date_stop.is_(None))
                
            if count_dto.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(territory=count_dto.territory, srid=4326)
                query = query.filter(func.ST_Intersects(Organizations.shape, territory_geom))
                
            count = (await self._session.execute(query)).scalar()
            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при : {e}")
            raise
        

class KkmsRepo(BaseRepository):
    model = Kkms

    async def get_by_bbox(self, dto: Bbox):
        # 71.389166,51.117415,71.390796,51.118253

        try:
            query = text(
                f"SELECT t.id, organization_id, reg_number, t.shape, o.name_ru, o.iin_bin FROM {self.model.__tablename__} t LEFT JOIN organizations o ON t.organization_id = o.id WHERE t.shape && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, :srid);"
            ).bindparams(minx=dto.bbox[0], miny=dto.bbox[1], maxx=dto.bbox[2], maxy=dto.bbox[3], srid=dto.srid)

            result = await self._session.execute(query)

            records = result.fetchall()

            logger.info(f"Найдено {len(records)} записей.")

            objects = []
            for record in records:
                obj = {
                    "id": record[0],
                    "organization_id": record[1],
                    "reg_number": record[2],
                    "shape": wkb_to_geojson(record[3]),
                    "name_ru": record[4],
                    "iin_bin": record[5],
                }
                objects.append(obj)

            return objects
        except SQLAlchemyError as e:
            logger.error(e)
            logger.error(f"Ошибка при поиске записей по bbox {dto}: {e}")
            raise

    async def filter(self, filters: KkmsFilterDto):
        try:
            query = select(self.model)

            if filters.territory is not None:
                query = query.filter(Kkms.shape.ST_Intersects("SRID=4326;" + filters.territory))

            if filters.reg_number is not None:
                query = query.filter(Kkms.reg_number == filters.reg_number)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей.")

            # If no records found return empty list
            if not records:
                return []

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise


class FnoTypesRepo(BaseRepository):
    model = FnoTypes


class FnoRepo(BaseWithOrganizationRepository):
    model = Fno
    
    async def get_fno_aggregation_statistics(self, filters: CountByTerritoryAndRegionsDto, current_year: int, prev_year: int):
        try:
            turnover_expr = (
                Fno.fno_100_00 + Fno.fno_110_00 + Fno.fno_150_00 + Fno.fno_180_00 +
                Fno.fno_220_00 + Fno.fno_300_00 + Fno.fno_910_00 + Fno.fno_911_00 +
                Fno.fno_912_00 + Fno.fno_913_00 + Fno.fno_920_00
            )
            
            query = (
                select(
                    func.coalesce(
                        func.sum(
                            case(
                                (Fno.year == current_year, turnover_expr),
                                else_=0.0,
                            )
                        ),
                        0.0,
                    ).label("turnover_current_year"),
                    func.coalesce(
                        func.sum(
                            case(
                                (Fno.year == prev_year, turnover_expr),
                                else_=0.0,
                            )
                        ),
                        0.0,
                    ).label("turnover_prev_year"),
                )
                .select_from(Fno)
            )
            
            if filters.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(territory=filters.territory, srid=4326)
                
                query = query.join(
                    Organizations, Fno.organization_id == Organizations.id
                ).where(
                    func.ST_Intersects(Organizations.shape, territory_geom)
                )

            result = await self._session.execute(query)
            return result.one()
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при cуммирований всех записей по фильтрам {filters}: {e}")
            raise

    async def get_fno_bar_chart_data(self, filters: CountByTerritoryAndRegionsDto, year: int):
        """Get FNO data by individual fields for bar chart"""
        try:
            # Define FNO fields and their codes
            fno_fields = [
                ("100.00", Fno.fno_100_00),
                ("110.00", Fno.fno_110_00),
                ("150.00", Fno.fno_150_00),
                ("180.00", Fno.fno_180_00),
                ("220.00", Fno.fno_220_00),
                ("300.00", Fno.fno_300_00),
                ("910.00", Fno.fno_910_00),
                ("911.00", Fno.fno_911_00),
                ("912.00", Fno.fno_912_00),
                ("913.00", Fno.fno_913_00),
                ("920.00", Fno.fno_920_00),
            ]
            
            # Build query to sum each FNO field separately
            select_items = []
            for code, field in fno_fields:
                select_items.append(
                    func.coalesce(func.sum(field), 0.0).label(f"fno_{code.replace('.', '_')}")
                )
            
            query = (
                select(*select_items)
                .select_from(Fno)
                .where(Fno.year == year)
            )
            
            # Apply territory filter if not RK
            if filters.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(territory=filters.territory, srid=4326)
                
                query = query.join(
                    Organizations, Fno.organization_id == Organizations.id
                ).where(
                    func.ST_Intersects(Organizations.shape, territory_geom)
                )
            
            result = await self._session.execute(query)
            row = result.one()
            
            # Format result as list of dictionaries
            chart_data = []
            for code, _ in fno_fields:
                field_name = f"fno_{code.replace('.', '_')}"
                amount = getattr(row, field_name, 0.0)
                chart_data.append({"fno_code": code, "amount": float(amount)})

            return chart_data

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных для столбчатой диаграммы ФНО: {e}")
            raise


class EsfSellerRepo(BaseWithOrganizationRepository):
    model = EsfSeller


class EsfSellerDailyRepo(BaseWithOrganizationRepository):
    model = EsfSellerDaily


class EsfBuyerRepo(BaseWithOrganizationRepository):
    model = EsfBuyer


class EsfBuyerDailyRepo(BaseWithOrganizationRepository):
    model = EsfBuyerDaily


class EsfStatisticsRepo(BaseWithOrganizationRepository):
    model = BaseModel
    
    def generate_organizations_cte(self, territory: str):
        territory_geom = territory_to_geo_element(territory=territory, srid=4326)
        
        organization_cte = select(
            Organizations.id.label("org_id")
        ).where(
            func.ST_Intersects(Organizations.shape, territory_geom) 
        ).cte("esf_cte")
        
        return organization_cte
    
    def generate_esf_statistics_subq(self, filters: CountByTerritoryAndRegionsDto, model: BaseModel):
        query = select(
            literal(model.__tablename__).label("source"),
            func.coalesce(func.sum(model.total_amount), 0).label("turnover")
        )
        
        if filters.region != RegionEnum.rk:
            organization_cte = self.generate_organizations_cte(territory=filters.territory)
            query = query.join(organization_cte, model.organization_id == organization_cte.c.org_id)
        
        return query
    
    def generate_esf_monthly_statistics_subg(self, filters: ByYearAndRegionsFilterDto, model: BaseModel):        
        query = select(
            literal(model.__tablename__).label("source"),
            model.month_year.label("date_"),
            func.coalesce(func.sum(model.total_amount), 0).label("turnover")
        ).where(
            model.month_year >= filters.period_start,
            model.month_year <= filters.period_end
        ).group_by(
           model.month_year 
        ).order_by(
           model.month_year 
        )
        
        if filters.region != RegionEnum.rk:
            organization_cte = self.generate_organizations_cte(territory=filters.territory)
            query = query.join(organization_cte, model.organization_id == organization_cte.c.org_id)

        return query
    
    async def get_esf_statistics(self, filters: CountByTerritoryAndRegionsDto):
        try:
            esf_seller_subq = self.generate_esf_statistics_subq(
                filters=filters, model=EsfSeller
            )
            
            esf_seller_daily_subq = self.generate_esf_statistics_subq(
                filters=filters, model=EsfSellerDaily
            )
            
            esf_buyer_subq = self.generate_esf_statistics_subq(
                filters=filters, model=EsfBuyer
            )
            
            esf_buyer_daily_subq = self.generate_esf_statistics_subq(
                filters=filters, model=EsfBuyerDaily
            )
            
            union_query = union_all(
                esf_seller_subq,
                esf_seller_daily_subq,
                esf_buyer_subq,
                esf_buyer_daily_subq,
            ).alias("stats")
                        
            rows = (
                await self._session.execute(select(union_query))
            ).mappings().all()

            result = {row["source"]: row for row in rows}
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при суммирований данных: {e}")
            raise
        
    async def get_esf_statistics_monthly(self, filters: ByYearAndRegionsFilterDto):
        try:
            esf_seller_month_subq = self.generate_esf_monthly_statistics_subg(
                filters=filters, model=EsfSellerMonth
            )
            
            esf_buyer_month_subq = self.generate_esf_monthly_statistics_subg(
                filters=filters, model=EsfBuyerMonth
            )
            
            union_query = union_all(
                esf_seller_month_subq,
                esf_buyer_month_subq
            ).alias("stats")
            
            rows = (
                await self._session.execute(select(union_query))
            ).mappings().all()

            result = defaultdict(list)
            for row in rows:
                result[row["source"]].append(row)

            return result
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при суммирований данных: {e}")
            raise
            

class RiskInfosRepo(BaseWithOrganizationRepository):
    model = RiskInfos

    async def get_latest_by_organization_id(self, id: int):
        try:
            max_date_subquery = select(func.max(RiskInfos.calculated_at)).scalar_subquery()
            query = select(self.model).filter_by(organization_id=id).filter(RiskInfos.calculated_at == max_date_subquery)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            # logger.info(f"Найдено {len(record)} записей.")

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по organization_id {id}: {e}")
            raise


class ReceiptsDailyRepo(BaseWithKkmRepository):
    model = ReceiptsDaily

    async def get_by_date_kkm_id(self, id: int, date: str):
        try:
            query = select(self.model).filter_by(kkms_id=id, date_check=date)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            logger.info(f"Найдено {self.model.__name__} с ID {id} записей.")

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по kkm_id {id}: {e}")
            raise

    async def get_sum_by_month_kkms(self, kkm_ids: list[int], year: int):
        try:
            query = (
                select(
                    func.extract("month", ReceiptsDaily.date_check).label("month"),
                    func.sum(ReceiptsDaily.check_sum).label("check_sum"),
                    func.count(ReceiptsDaily.check_count).label("check_count"),
                )
                .filter(ReceiptsDaily.kkms_id.in_(kkm_ids))
                .filter(func.extract("year", ReceiptsDaily.date_check) == year)
                .group_by(func.extract("month", ReceiptsDaily.date_check))
            )
            result = await self._session.execute(query)
            record = result.fetchall()

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по kkm_id {id}: {e}")
            raise


class ReceiptsAnnualRepo(BaseWithKkmRepository):
    model = ReceiptsAnnual

    async def get_by_year_kkm_id(self, id: int, year: int):
        try:
            query = select(self.model).filter_by(kkms_id=id, year=year)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по kkm_id {id}: {e}")
            raise


class ReceiptsRepo(BaseWithKkmRepository):
    model = Receipts

    async def get_by_fiscal_and_kkm_reg_number(self, fiskal_sign: int, kkm_reg_number: str):
        try:
            query = select(self.model).join(Kkms).filter(Receipts.fiskal_sign == fiskal_sign, Kkms.reg_number == kkm_reg_number)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей.")

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_by_fiscal_and_kkm_serial_number(self, fiskal_sign: int, kkm_serial_number: str):
        try:
            query = (
                select(self.model).join(Kkms).filter(Receipts.fiskal_sign == fiskal_sign, Kkms.serial_number == kkm_serial_number)
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_by_fiscal_and_iin_bin(self, fiskal_sign: int, kkm_iin_bin: str):
        try:
            query = (
                select(self.model)
                .join(Kkms)
                .join(Organizations)
                .filter(Receipts.fiskal_sign == fiskal_sign, Organizations.iin_bin == kkm_iin_bin)
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей.")

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_summary_by_kkm_id(self, id: int):
        try:
            query = (
                select(
                    Receipts.kkms_id,
                    func.sum(Receipts.full_item_price).label("check_sum"),
                    func.count(distinct(Receipts.fiskal_sign)).label("check_count"),
                )
                .join(Kkms)
                .filter(Kkms.id == id)
                .group_by(Receipts.kkms_id)
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise