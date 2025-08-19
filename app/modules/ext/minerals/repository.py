from sqlalchemy import select, func

from app.modules.common.repository import BaseExtRepository
from app.modules.common.dto import TerritoryFilterDto
from app.modules.common.utils import territory_to_geo_element
from app.modules.ext.minerals.dtos import (
    MineralsLocContractsFilterDto,
    IucMineralsFilterRequestDto
)
from app.modules.ckf.models import Organizations
from .models import MineralsLocContracts, IucMinerals, IucLocTypes
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError


class MineralsLocContractsRepo(BaseExtRepository):
    model = MineralsLocContracts

    async def filter(self, filters: MineralsLocContractsFilterDto):
        try:
            query = select(self.model)

            if filters.territory is not None:
                query = query.filter(MineralsLocContracts.geom.ST_Intersects("SRID=4326;" + filters.territory))

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

class IucMineralsRepo(BaseExtRepository):
    model = IucMinerals

    async def get_filters(self):
        try:
            query = (
                select(
                    IucLocTypes.id,
                    IucLocTypes.loc_type
                )
                .select_from(
                    IucLocTypes
                )
            )

            result = await self._session.execute(query)
            rows = result.all()

            return {
                'filters':
                    [dict(row._mapping) for row in rows]
            }
        except SQLAlchemyError as e:
           logger.error(f"Ошибка при поиске всех фильтров: {e}")
           raise  

    async def get_minerals_info_by_id(self, id: int):
        try:
            query = (
                select(
                    IucMinerals.loc_number,
                    IucLocTypes.loc_type,
                    IucMinerals.loc_date,
                    IucMinerals.official_org_xin,
                    IucMinerals.official_org_name,
                    IucMinerals.loc_status,
                    Organizations.name_ru,
                    Organizations.iin_bin,
                    Organizations.address
                )
                .select_from(IucMinerals)
                .join(
                    IucLocTypes,
                    IucMinerals.loc_type_id == IucLocTypes.id
                )
                .join(
                    Organizations,
                    IucMinerals.organization_id == Organizations.id
                )
                .where(
                    IucMinerals.id == id
                )
            )

            result = await self._session.execute(query)
            response = dict(result.mappings().one())

            return response

        except SQLAlchemyError as e:
           logger.error(f"Ошибка при поиске записей по id {id}: {e}")
           raise  

    async def get_contracts_by_territory(self, filter: TerritoryFilterDto):
        territory_geom = territory_to_geo_element(filter.territory)
        try:
            query = (
                select(
                    IucMinerals.id,
                    IucMinerals.loc_number,
                    Organizations.name_ru,
                    IucLocTypes.loc_type
                )
                .select_from(
                    IucMinerals
                )
                .join(
                    IucLocTypes,
                    IucMinerals.loc_type_id == IucLocTypes.id
                )
                .join(
                    Organizations,
                    IucMinerals.organization_id == Organizations.id
                )
                .where(
                    func.ST_Intersects(
                        IucMinerals.shape,
                        territory_geom
                    )
                )
            )

            result = await self._session.execute(query)
            rows = result.all()

            return {
                'contracts':
                    [dict(row._mapping) for row in rows]
            }
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filter}: {e}")
            raise  