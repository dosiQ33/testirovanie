"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import status, HTTPException
from sqlalchemy import distinct, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.dto import Bbox
from app.modules.common.repository import BaseRepository, BaseWithKkmRepository, BaseWithOrganizationRepository
from app.modules.common.utils import wkb_to_geojson
from .dtos import KkmsFilterDto, OrganizationsFilterDto
from .models import (
    EsfBuyer,
    EsfBuyerDaily,
    EsfSeller,
    EsfSellerDaily,
    Organizations,
    Kkms,
    Receipts,
    ReceiptsAnnual,
    ReceiptsDaily,
    RiskInfos,
)


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

            # logger.info(f"Найдено {len(record)} записей.")

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
