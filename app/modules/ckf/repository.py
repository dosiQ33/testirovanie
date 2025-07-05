"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import status, HTTPException
from sqlalchemy import distinct, func, select, text, or_, cast, Integer, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.dto import Bbox
from app.modules.common.repository import BaseRepository, BaseWithKkmRepository, BaseWithOrganizationRepository
from app.modules.common.utils import wkb_to_geojson
from app.modules.ext.kazgeodesy.models import KazgeodesyRkOblasti, KazgeodesyRkRaiony #осторожно
from .dtos import KkmsFilterDto, OrganizationsFilterDto, ByYearAndRegionsFilterDto, CountByRegionsDto
from .models import (
    EsfBuyer,
    EsfBuyerDaily,
    EsfSeller,
    EsfSellerDaily,
    Fno,
    FnoTypes,
    Organizations,
    Kkms,
    Receipts,
    ReceiptsAnnual,
    ReceiptsDaily,
    RiskInfos,
    Populations
)
from .enums import RegionEnum
from typing import List, Optional
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

            query = (
                select(
                    cast(func.extract("month", month_start), Integer).label("month"),
                    func.count().label("count")
                )
                .select_from(
                    month_series
                    .join(
                        Organizations,
                        and_(
                            Organizations.date_start <= month_end,
                            or_(
                                Organizations.date_stop.is_(None),
                                Organizations.date_stop > month_end
                            ),
                            Organizations.shape.ST_Intersects("SRID=4326;" + filters.territory)
                        )
                    )
                )
                .group_by(month_start)
                .order_by(month_start)
            )

            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "count": row.count} for row in rows]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise

    async def count_by_year_and_regions(self, territory: str, date_: Optional[date]):
        try:
            query = select(func.count()).select_from(Organizations).filter(Organizations.shape.ST_Intersects("SRID=4326;" + territory))
            
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


class EsfSellerRepo(BaseWithOrganizationRepository):
    model = EsfSeller


class EsfSellerDailyRepo(BaseWithOrganizationRepository):
    model = EsfSellerDaily


class EsfBuyerRepo(BaseWithOrganizationRepository):
    model = EsfBuyer


class EsfBuyerDailyRepo(BaseWithOrganizationRepository):
    model = EsfBuyerDaily


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

class PopulationRepo(BaseRepository):
    model = Populations
    
    def apply_region_join(self, query, region: RegionEnum, territory: str):
        if region == RegionEnum.oblast:
            return (
                query.join(
                    KazgeodesyRkOblasti,
                    Populations.oblast_id == KazgeodesyRkOblasti.id
                ).filter(func.ST_Intersects(KazgeodesyRkOblasti.geom, territory))
            )
        else:
            return (
                query.join(
                    KazgeodesyRkRaiony,
                    Populations.raion_id == KazgeodesyRkRaiony.id
                ).filter(func.ST_Intersects(KazgeodesyRkRaiony.geom, territory))
            )
    
    async def get_population_monthly_by_region(self, region: RegionEnum, filters: ByYearAndRegionsFilterDto):
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
            
            query = self.apply_region_join(query=query, region=region, territory=filters.territory)
            result = await self._session.execute(query)
            rows = result.all()

            return [{"month": row.month, "count": row.count} for row in rows]
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise
        
    async def get_many_past_year_by_region(self, count_dto: CountByRegionsDto, date_: date):
        try:
            query = select(Populations).filter(Populations.date_ == date_)
            query = self.apply_region_join(query=query, region=count_dto.region, territory=count_dto.territory)
            
            result = await self._session.execute(query)
            records = result.scalars().all()
            
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_many_current_year_maximum_by_region(self, count_dto: CountByRegionsDto):
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

    async def get_many_current_year_in_by_region(self, count_dto: CountByRegionsDto, dates: List[date]):
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