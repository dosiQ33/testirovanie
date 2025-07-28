"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import status, HTTPException
from sqlalchemy import (
    distinct,
    func,
    select,
    text,
    or_,
    cast,
    Integer,
    and_,
    union_all,
    literal,
    case,
    Text,
    DateTime,
    Numeric,
    desc,
)
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2.functions import ST_Within

from loguru import logger
from collections import defaultdict

from app.modules.common.dto import (
    Bbox,
    ByYearAndRegionsFilterDto,
    CountByTerritoryAndRegionsDto,
    CountByYearAndRegionsDto,
    TerritoryFilterDto,
)
from app.modules.common.repository import (
    BaseRepository,
    BaseWithKkmRepository,
    BaseWithOrganizationRepository,
)
from app.modules.common.utils import wkb_to_geojson, territory_to_geo_element
from app.modules.common.models import BaseModel
from app.modules.common.enums import RegionEnum, FloorEnum
from .dtos import (
    KkmsFilterDto,
    OrganizationsFilterDto,
    BuildingsFilterDto,
    KkmStatisticsRequestDto,
)
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
    RiskInfos,
    DicSzpt,
    ReceiptsMonthly
)
from typing import Optional
from datetime import date, datetime


class OrganizationsRepo(BaseRepository):
    model = Organizations

    async def get_by_bbox(self, dto: Bbox):
        # 71.389166,51.117415,71.390796,51.118253

        try:
            query = text(
                f"SELECT id, iin_bin, name_ru, shape FROM {self.model.__tablename__} WHERE shape && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, :srid);"
            ).bindparams(
                minx=dto.bbox[0],
                miny=dto.bbox[1],
                maxx=dto.bbox[2],
                maxy=dto.bbox[3],
                srid=dto.srid,
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Организация не найдена"
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при поиске филиалов",
            )

    async def filter(self, filters: OrganizationsFilterDto):
        try:
            query = select(self.model)

            if filters.territory is not None:
                query = query.filter(
                    Organizations.shape.ST_Intersects("SRID=4326;" + filters.territory)
                )

            if filters.iin_bin is not None:
                query = query.filter(Organizations.iin_bin == filters.iin_bin)

            if filters.oked_ids is not None:
                query = query.filter(Organizations.oked_id.in_(filters.oked_ids))

            if filters.risk_degree_ids is not None:
                query = query.join(RiskInfos).filter(
                    RiskInfos.risk_degree_id.in_(filters.risk_degree_ids)
                )

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

    async def count_monthly_by_year_and_regions(
        self, filters: ByYearAndRegionsFilterDto
    ):
        try:
            month_series = select(
                func.generate_series(
                    filters.period_start, filters.period_end, text("interval '1 month'")
                ).label("month_start")
            ).cte("month_series")

            month_col = month_series.c.month_start
            month_start = func.date_trunc("month", month_col)
            month_end = (
                month_start + text("interval '1 month'") - text("interval '1 day'")
            )

            conditions = [
                Organizations.date_start <= month_end,
                or_(
                    Organizations.date_stop.is_(None),
                    Organizations.date_stop > month_end,
                ),
            ]

            if filters.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(
                    territory=filters.territory, srid=4326
                )
                conditions.append(
                    func.ST_Intersects(Organizations.shape, territory_geom)
                )

            join_on = and_(*conditions)
            query = (
                select(
                    cast(func.extract("month", month_start), Integer).label("month"),
                    func.count().label("count"),
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

    async def count_by_year_and_regions(
        self, count_dto: CountByYearAndRegionsDto, date_: Optional[date]
    ):
        try:
            query = select(func.count()).select_from(Organizations)

            if date_:
                query = query.filter(
                    Organizations.date_start <= date_,
                    or_(
                        Organizations.date_stop.is_(None),
                        Organizations.date_stop > date_,
                    ),
                )
            else:
                query = query.filter(Organizations.date_stop.is_(None))

            if count_dto.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(
                    territory=count_dto.territory, srid=4326
                )
                query = query.filter(
                    func.ST_Intersects(Organizations.shape, territory_geom)
                )

            count = (await self._session.execute(query)).scalar()
            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при : {e}")
            raise

    async def get_all_organizations_by_building(self, filter: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(territory=filter.territory)
        try:
            query = (
                select(func.count())
                .select_from(Organizations)
                .where(
                    and_(
                        ST_Within(Organizations.shape, territory_geom),
                        Organizations.date_stop.is_(None),
                    )
                )
            )

            count = (await self._session.execute(query)).scalar()
            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при : {e}")
            raise

    async def get_organizations_info_by_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(territory=filters.territory)
        try:
            query = (
                select(
                    Organizations.iin_bin,
                    Organizations.name_ru,
                    func.coalesce(EsfSeller.total_amount, 0).label(
                        "seller_total_amount"
                    ),
                    func.coalesce(EsfBuyer.total_amount, 0).label("buyer_total_amount"),
                    func.coalesce(func.sum(ReceiptsAnnual.check_sum), 0).label("kkm_total_amount"),
                )
                .outerjoin(EsfSeller, Organizations.id == EsfSeller.organization_id)
                .outerjoin(EsfBuyer, Organizations.id == EsfBuyer.organization_id)
                .outerjoin(Kkms, Organizations.id == Kkms.organization_id)
                .outerjoin(ReceiptsAnnual, Kkms.id == ReceiptsAnnual.kkms_id)
                .where(
                    ST_Within(Organizations.shape, territory_geom),
                    Organizations.date_stop.is_(None),
                    Kkms.date_stop.is_(None),
                )
                .group_by(
                    Organizations.iin_bin,
                    Organizations.name_ru,
                    EsfSeller.total_amount,
                    EsfBuyer.total_amount,
                )
            )

            result = await self._session.execute(query)
            rows = result.all()

            rows = [dict(row._mapping) for row in rows]
            return rows
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
            ).bindparams(
                minx=dto.bbox[0],
                miny=dto.bbox[1],
                maxx=dto.bbox[2],
                maxy=dto.bbox[3],
                srid=dto.srid,
            )

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
                query = query.filter(
                    Kkms.shape.ST_Intersects("SRID=4326;" + filters.territory)
                )

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

    async def get_kkms_in_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(territory=filters.territory)
        try:
            query = (
                select(func.count())
                .select_from(Kkms)
                .join(
                    Organizations,
                    Kkms.organization_id == Organizations.id
                )
                .where(
                    and_(
                        ST_Within(Organizations.shape, territory_geom), Kkms.date_stop.is_(None)
                    )
                )
            )

            count = (await self._session.execute(query)).scalar()
            return count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise

#
    async def get_kkms_by_month(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(territory=filters.territory)
        try:
            month_trunc = cast(func.extract("month", ReceiptsMonthly.month), Integer).label(
                "month"
            )

            columns = [month_trunc]

            columns.append(func.round(func.sum(func.cast(ReceiptsMonthly.check_sum, Numeric)), 2).label("turnover"))

            if filters.floor == FloorEnum.kkm:
                columns.append(
                    func.count(ReceiptsMonthly.check_count).label("check_count")
                )

            query = (
                select(*columns)
                .join(Kkms, ReceiptsMonthly.kkms_id == Kkms.id)
                .join(Organizations, Kkms.organization_id == Organizations.id)
                .where(
                    ST_Within(Kkms.shape, territory_geom),
                    func.extract("year", ReceiptsMonthly.month) == 2025,
                )
                .group_by(month_trunc)
                .order_by(month_trunc)
            )

            if filters.floor == FloorEnum.np:
                query.where(Kkms.date_stop.is_(None))
            else:
                query.where(Organizations.date_stop.is_(None))

            result = await self._session.execute(query)
            rows = result.all()
            response = []

            for row in rows:
                row_data = {
                    "month": row.month,
                    "turnover": row.turnover,
                }
                if filters.floor == FloorEnum.kkm:
                    row_data["check_count"] = row.check_count

                response.append(row_data)

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise

    async def get_kkm_info_by_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(filters.territory)
        try:
            query = (
                select(
                    Organizations.iin_bin,
                    Kkms.reg_number,
                    func.sum(ReceiptsDaily.check_sum).label("daily_sum"),
                    func.sum(ReceiptsDaily.check_count).label("daily_count"),
                    func.sum(ReceiptsAnnual.check_sum).label("annual_sum"),
                    func.sum(ReceiptsAnnual.check_count).label("annual_count"),
                )
                .select_from(Organizations)
                .join(Kkms, Organizations.id == Kkms.organization_id)
                .join(ReceiptsDaily, Kkms.id == ReceiptsDaily.kkms_id)
                .join(ReceiptsAnnual, Kkms.id == ReceiptsAnnual.kkms_id)
                .where(
                    Kkms.date_stop.is_(None),
                    ST_Within(Kkms.shape, territory_geom),
                )
                .group_by(Organizations.iin_bin, Kkms.reg_number)
            )

            result = await self._session.execute(query)
            rows = result.all()

            rows = [dict(row._mapping) for row in rows]
            return {"info": [row for row in rows]}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise


class FnoTypesRepo(BaseRepository):
    model = FnoTypes


class FnoRepo(BaseWithOrganizationRepository):
    model = Fno

    async def get_fno_aggregation_statistics(
        self, filters: CountByTerritoryAndRegionsDto, current_year: int, prev_year: int
    ):
        try:
            turnover_expr = (
                Fno.fno_100_00
                + Fno.fno_110_00
                + Fno.fno_150_00
                + Fno.fno_180_00
                + Fno.fno_220_00
                + Fno.fno_300_00
                + Fno.fno_910_00
                + Fno.fno_911_00
                + Fno.fno_912_00
                + Fno.fno_913_00
                + Fno.fno_920_00
            )

            query = select(
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
            ).select_from(Fno)

            if filters.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(
                    territory=filters.territory, srid=4326
                )

                query = query.join(
                    Organizations, Fno.organization_id == Organizations.id
                ).where(func.ST_Intersects(Organizations.shape, territory_geom))

            result = await self._session.execute(query)
            return result.one()

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при cуммирований всех записей по фильтрам {filters}: {e}"
            )
            raise

    async def get_fno_bar_chart_data(
        self, filters: CountByTerritoryAndRegionsDto, year: int
    ):
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
                    func.coalesce(func.sum(field), 0.0).label(
                        f"fno_{code.replace('.', '_')}"
                    )
                )

            query = select(*select_items).select_from(Fno).where(Fno.year == year)

            # Apply territory filter if not RK
            if filters.region != RegionEnum.rk:
                territory_geom = territory_to_geo_element(
                    territory=filters.territory, srid=4326
                )

                query = query.join(
                    Organizations, Fno.organization_id == Organizations.id
                ).where(func.ST_Intersects(Organizations.shape, territory_geom))

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
            logger.error(
                f"Ошибка при получении данных для столбчатой диаграммы ФНО: {e}"
            )
            raise

    async def get_fno_bar_char_by_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(filters.territory)
        try:
            query = (
                select(
                    Fno.type_id.label("quarter"),
                    func.sum(Fno.fno_910_00 + Fno.fno_300_00).label("total_sum"),
                )
                .join(Organizations, Fno.organization_id == Organizations.id)
                .where(
                    Fno.type_id.in_([1, 2, 3, 4]),
                    func.ST_Intersects(Organizations.shape, territory_geom),
                    Organizations.date_stop.is_(None),
                )
                .group_by(Fno.type_id)
                .order_by(Fno.type_id)
            )

            result = await self._session.execute(query)
            rows = result.all()

            rows = [dict(row._mapping) for row in rows]

            return {"quarterly": [row for row in rows]}

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при получении данных для столбчатой диаграммы ФНО: {e}"
            )
            raise

    async def get_fno_info_by_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(filters.territory)
        try:
            query = (
                select(
                    Organizations.iin_bin,
                    func.sum(
                        case(
                            (Fno.type_id == 1, Fno.fno_300_00 + Fno.fno_913_00), else_=0
                        )
                    ).label("q1_sum"),
                    func.sum(
                        case(
                            (Fno.type_id == 2, Fno.fno_300_00 + Fno.fno_913_00), else_=0
                        )
                    ).label("q2_sum"),
                    func.sum(
                        case(
                            (Fno.type_id == 3, Fno.fno_300_00 + Fno.fno_913_00), else_=0
                        )
                    ).label("q3_sum"),
                    func.sum(
                        case(
                            (Fno.type_id == 4, Fno.fno_300_00 + Fno.fno_913_00), else_=0
                        )
                    ).label("q4_sum"),
                    func.sum(case((Fno.type_id == 5, Fno.fno_910_00), else_=0)).label(
                        "half1_sum"
                    ),
                    func.sum(case((Fno.type_id == 6, Fno.fno_910_00), else_=0)).label(
                        "half2_sum"
                    ),
                    func.sum(case((Fno.type_id == 0, Fno.fno_920_00), else_=0)).label(
                        "year_sum"
                    ),
                )
                .join(Organizations, Fno.organization_id == Organizations.id)
                .where(
                    Organizations.date_stop.is_(None),
                    func.ST_Intersects(Organizations.shape, territory_geom),
                    Fno.year == 2025,
                )
                .group_by(Organizations.iin_bin)
            )

            result = await self._session.execute(query)
            rows = result.all()

            rows = [dict(row._mapping) for row in rows]
            return {"info": [row for row in rows]}
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при получении данных для столбчатой диаграммы ФНО: {e}"
            )
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

    def generate_organizations_cte(
        self, region: RegionEnum, territory: str, cte_name: str
    ):
        territory_geom = territory_to_geo_element(territory=territory, srid=4326)

        organization_cte = select(Organizations.id.label("org_id")).where(
            func.ST_Intersects(Organizations.shape, territory_geom)
        )

        if region == RegionEnum.building:
            organization_cte = organization_cte.where(Organizations.date_stop.is_(None))

        organization_cte = organization_cte.cte(cte_name)

        return organization_cte

    def generate_esf_statistics_subq(
        self, filters: CountByTerritoryAndRegionsDto, model: BaseModel
    ):
        select_items = [
            literal(model.__tablename__).label("source"),
            func.round(func.coalesce(func.sum(model.total_amount.cast(Numeric)), 0), 2).label("turnover"),
        ]

        query = select(*select_items)

        if filters.region != RegionEnum.rk:
            cte_name = f"esf_cte_{model.__tablename__}"
            organization_cte = self.generate_organizations_cte(
                region=filters.region, territory=filters.territory, cte_name=cte_name
            )
            query = query.join(
                organization_cte, model.organization_id == organization_cte.c.org_id
            )

        return query

    def generate_esf_monthly_statistics_subg(
        self, filters: ByYearAndRegionsFilterDto, model: BaseModel
    ):
        query = (
            select(
                literal(model.__tablename__).label("source"),
                model.month_year.label("date_"),
                func.coalesce(func.sum(model.total_amount), 0).label("turnover"),
            )
            .where(
                model.month_year >= filters.period_start,
                model.month_year <= filters.period_end,
            )
            .group_by(model.month_year)
            .order_by(model.month_year)
        )

        if filters.region != RegionEnum.rk:
            cte_name = f"esf_cte_{model.__tablename__}"
            organization_cte = self.generate_organizations_cte(
                region=filters.region, territory=filters.territory, cte_name=cte_name
            )
            query = query.join(
                organization_cte, model.organization_id == organization_cte.c.org_id
            )

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

            rows = (await self._session.execute(select(union_query))).mappings().all()

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

            union_query = union_all(esf_seller_month_subq, esf_buyer_month_subq).alias(
                "stats"
            )

            rows = (await self._session.execute(select(union_query))).mappings().all()

            result = defaultdict(list)
            for row in rows:
                result[row["source"]].append(row)

            return result

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при суммирований данных: {e}")
            raise

    async def get_esf_info_by_building(self, filters: BuildingsFilterDto):
        territory_geom = territory_to_geo_element(filters.territory)
        try:
            query = (
                select(
                    Organizations.iin_bin,
                    Organizations.name_ru,
                    func.coalesce(EsfSellerDaily.total_amount, 0).label(
                        "seller_daily_total"
                    ),
                    func.coalesce(EsfBuyerDaily.total_amount, 0).label(
                        "buyer_daily_total"
                    ),
                    func.coalesce(EsfSeller.total_amount, 0).label("seller_total"),
                    func.coalesce(EsfBuyer.total_amount, 0).label("buyer_total"),
                )
                .outerjoin(
                    EsfSellerDaily, Organizations.id == EsfSellerDaily.organization_id
                )
                .outerjoin(
                    EsfBuyerDaily, Organizations.id == EsfBuyerDaily.organization_id
                )
                .outerjoin(EsfSeller, Organizations.id == EsfSeller.organization_id)
                .outerjoin(EsfBuyer, Organizations.id == EsfBuyer.organization_id)
                .where(
                    func.ST_Intersects(Organizations.shape, territory_geom),
                    Organizations.date_stop.is_(None),
                )
                .group_by(
                    Organizations.iin_bin,
                    Organizations.name_ru,
                    EsfSellerDaily.total_amount,
                    EsfBuyerDaily.total_amount,
                    EsfSeller.total_amount,
                    EsfBuyer.total_amount,
                )
            )

            result = await self._session.execute(query)
            rows = result.all()

            rows = [dict(row._mapping) for row in rows]
            return rows
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при сборе данных: {e}")
            raise


class RiskInfosRepo(BaseWithOrganizationRepository):
    model = RiskInfos

    async def get_latest_by_organization_id(self, id: int):
        try:
            max_date_subquery = select(
                func.max(RiskInfos.calculated_at)
            ).scalar_subquery()
            query = (
                select(self.model)
                .filter_by(organization_id=id)
                .filter(RiskInfos.calculated_at == max_date_subquery)
            )
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            # logger.info(f"Найдено {len(record)} записей.")

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по organization_id {id}: {e}")
            raise


class ReceiptsDailyRepo(BaseWithKkmRepository):
    model = ReceiptsDaily

    async def get_by_date_kkm_id(self, id: int):
        try:
            query = select(self.model).filter_by(kkms_id=id)
            result = await self._session.execute(query)
            record = result.scalars().first()

            logger.info(f"Найдено {self.model.__name__} с ID {id} записей.")

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

    async def get_by_fiscal_and_kkm_reg_number(
        self, fiskal_sign: int, kkm_reg_number: str
    ):
        try:
            query = (
                select(self.model)
                .join(Kkms)
                .filter(
                    Receipts.fiskal_sign == fiskal_sign,
                    Kkms.reg_number == kkm_reg_number,
                )
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей.")

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_by_fiscal_and_kkm_serial_number(
        self, fiskal_sign: int, kkm_serial_number: str
    ):
        try:
            query = (
                select(self.model)
                .join(Kkms)
                .filter(
                    Receipts.fiskal_sign == fiskal_sign,
                    Kkms.serial_number == kkm_serial_number,
                )
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
                .filter(
                    Receipts.fiskal_sign == fiskal_sign,
                    Organizations.iin_bin == kkm_iin_bin,
                )
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

    async def get_monthly_statistics_by_territory(
        self, filters: KkmStatisticsRequestDto
    ):
        month_extract = func.extract(
            "month", func.to_timestamp(Receipts.operation_date, "YYYY-MM-DD HH24:MI:SS")
        )
        year_extract = func.extract(
            "year", func.to_timestamp(Receipts.operation_date, "YYYY-MM-DD HH24:MI:SS")
        )
        try:
            query = (
                select(
                    month_extract.label("month"),
                    func.count(
                        func.distinct(
                            func.concat(
                                Receipts.fiskal_sign.cast(Text),
                                Receipts.kkms_id.cast(Text),
                            )
                        )
                    ).label("receipts_count"),
                    func.sum(Receipts.full_item_price).label("turnover"),
                )
                .filter(year_extract == filters.year)
                .group_by(month_extract)
                .order_by(month_extract)
            )

            if filters.region != RegionEnum.rk:
                geom = territory_to_geo_element(filters.territory)
                query = (
                    query.join(Kkms, Receipts.kkms_id == Kkms.id)
                    .join(Organizations, Kkms.organization_id == Organizations.id)
                    .filter(func.ST_Intersects(Organizations.shape, geom))
                )

            result = await self._session.execute(query)
            records = result.all()

            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении месячной статистики по территории: {e}")
            raise

    async def get_aggregated_statistics_by_territory(
        self, territory_wkt, current_date: date
    ):
        try:

            current_year = current_date.year

            # Подзапрос для активных ККМ
            active_kkm_subq = (
                select(func.count(Kkms.id).label("active_count"))
                .select_from(Kkms)
                .filter(Kkms.date_stop.is_(None))
            )

            # Подзапрос для дневной статистики
            daily_stats_subq = (
                select(
                    func.coalesce(func.sum(ReceiptsDaily.check_sum), 0).label(
                        "daily_turnover"
                    ),
                    func.coalesce(func.sum(ReceiptsDaily.check_count), 0).label(
                        "daily_receipts_count"
                    ),
                )
                .select_from(ReceiptsDaily)
                .filter(ReceiptsDaily.date_check == current_date)
            )

            # Подзапрос для годовой статистики
            yearly_stats_subq = (
                select(
                    func.coalesce(func.sum(ReceiptsAnnual.check_sum), 0).label(
                        "yearly_turnover"
                    ),
                    func.coalesce(func.sum(ReceiptsAnnual.check_count), 0).label(
                        "yearly_receipts_count"
                    ),
                )
                .select_from(ReceiptsAnnual)
                .filter(ReceiptsAnnual.year == current_year)
            )

            # Применяем территориальную фильтрацию если территория указана
            if territory_wkt:
                active_kkm_subq = active_kkm_subq.join(
                    Organizations, Kkms.organization_id == Organizations.id
                ).filter(func.ST_Intersects(Organizations.shape, territory_wkt))
                daily_stats_subq = (
                    daily_stats_subq.join(Kkms, ReceiptsDaily.kkms_id == Kkms.id)
                    .join(Organizations, Kkms.organization_id == Organizations.id)
                    .filter(func.ST_Intersects(Organizations.shape, territory_wkt))
                )
                yearly_stats_subq = (
                    yearly_stats_subq.join(Kkms, ReceiptsAnnual.kkms_id == Kkms.id)
                    .join(Organizations, Kkms.organization_id == Organizations.id)
                    .filter(func.ST_Intersects(Organizations.shape, territory_wkt))
                )

            # Выполняем запросы
            active_count_result = await self._session.execute(active_kkm_subq)
            active_count = active_count_result.scalar() or 0

            daily_result = await self._session.execute(daily_stats_subq)
            daily_row = daily_result.one()

            yearly_result = await self._session.execute(yearly_stats_subq)
            yearly_row = yearly_result.one()

            return {
                "active_kkm_count": active_count,
                "daily_turnover": float(daily_row.daily_turnover),
                "daily_receipts_count": int(daily_row.daily_receipts_count),
                "yearly_turnover": float(yearly_row.yearly_turnover),
                "yearly_receipts_count": int(yearly_row.yearly_receipts_count),
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении агрегированной статистики ККМ: {e}")
            raise

    async def get_aggregated_statistics_by_building(
        self, territory: str, current_date: date
    ):
        try:
            daily_receipts_query = (
                select(
                    func.coalesce(func.sum(ReceiptsDaily.check_sum), 0).label(
                        "daily_turnover"
                    )
                )
                .select_from(ReceiptsDaily)
                .join(Kkms, ReceiptsDaily.kkms_id == Kkms.id)
                .filter(
                    Kkms.date_stop.is_(None),
                    # ReceiptsDaily.date_check == current_date,
                    func.ST_Within(Kkms.shape, territory),
                )
            )

            annual_receipts_query = (
                select(
                    func.coalesce(func.sum(ReceiptsAnnual.check_sum), 0).label(
                        "yearly_turnover"
                    )
                )
                .select_from(ReceiptsAnnual)
                .join(Kkms, ReceiptsAnnual.kkms_id == Kkms.id)
                .filter(
                    Kkms.date_stop.is_(None),
                    ReceiptsAnnual.year == current_date.year,
                    func.ST_Intersects(Kkms.shape, territory),
                )
            )

            daily_receipts_query_1 = (
                select(
                    func.coalesce(func.sum(ReceiptsDaily.check_sum), 0).label(
                        "daily_turnover"
                    ),
                    Kkms.reg_number
                )
                .select_from(ReceiptsDaily)
                .join(Kkms, ReceiptsDaily.kkms_id == Kkms.id)
                .filter(
                    Kkms.date_stop.is_(None),
                    # ReceiptsDaily.date_check == current_date,
                    func.ST_Within(Kkms.shape, territory),
                )
                .group_by(Kkms.reg_number)
            )

            daily_receipts_result = await self._session.execute(daily_receipts_query)
            daily_result = daily_receipts_result.one()
            
            daily_receipts_result_1 = await self._session.execute(daily_receipts_query_1)
            daily_result_1 = daily_receipts_result_1.mappings().all()

            print(daily_result_1)

            annual_receipts_result = await self._session.execute(annual_receipts_query)
            annual_result = annual_receipts_result.one()

            return {
                "daily_turnover": float(daily_result.daily_turnover),
                "yearly_turnover": float(annual_result.yearly_turnover),
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении агрегированной статистики ККМ: {e}")
            raise

class SzptRepo(BaseRepository):
    model = DicSzpt

    async def get_violations_count_by_kkm_id(self, kkm_id: int, szpt_id: int):
        try:
            query = (
                select(
                    func.count()
                )
                .select_from(Receipts)
                .where(
                    Receipts.kkms_id == kkm_id,
                    Receipts.has_szpt_violation == True,
                    Receipts.szpt_id == szpt_id
                )
            )

            result = await self._session.execute(query)
            row = result.one()

            return dict(row._mapping)
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при получении ККМ с нарушениями: {e}')
            raise

    async def get_last_receipt_with_violation(self, kkm_id: int, szpt_id: int):
        try:
            query_info = (
                select(
                    Kkms.reg_number,
                    Kkms.serial_number,
                    Receipts.fiskal_sign,
                    func.to_char(Receipts.operation_date, 'DD-MM-YYYY').label('date'),
                    func.to_char(Receipts.operation_date, 'HH24:MI:SS').label('time')
                )
                .join(
                    Receipts,
                    Kkms.id == Receipts.kkms_id
                )
                .where(
                    Kkms.id == kkm_id,
                    Receipts.szpt_id == szpt_id,
                    Receipts.has_szpt_violation.is_(True),
                )
                .order_by(desc(Receipts.operation_date))
                .limit(1)
            )

            result = await self._session.execute(query_info)
            row = result.one()

            return dict(row._mapping)
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при получении ККМ с нарушениями: {e}')
            raise  

    async def get_receipt_content(self, fiskal_sign: int):
        try:
            query = (
                select(
                    Receipts.item_name,
                    Receipts.item_nds,
                    Receipts.price_per_unit,
                    Receipts.current_max_price,
                    Receipts.full_item_price,
                    Receipts.payment_type,
                    func.coalesce(Receipts.has_szpt_violation, False).label('has_szpt_violation'),
                    DicSzpt.unit
                )
                .outerjoin(
                    DicSzpt,
                    Receipts.szpt_id == DicSzpt.id
                )
                .where(
                    Receipts.fiskal_sign == fiskal_sign
                )
            )

            result = await self._session.execute(query)
            rows = result.mappings().all()

            return {'products':
                    [dict(row) for row in rows],
                    }
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при получении ККМ с нарушениями: {e}')
            raise      