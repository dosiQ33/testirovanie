from sqlalchemy import select
from app.modules.common.repository import BaseExtRepository
from app.modules.ext.minerals.dtos import MineralsLocContractsFilterDto
from .models import MineralsLocContracts
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
