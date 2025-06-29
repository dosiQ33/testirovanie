from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
from loguru import logger
from app.modules.common.repository import BaseRepository
from .dtos import RisksFilterDto
from .models import (
    Risks,
    DicRiskDegree,
    DicRiskType,
    DicRiskName,
    DicOrderStatus,
    DicOrderType,
)
from app.modules.ckf.models import Organizations


class DicOrderStatusRepo(BaseRepository):
    model = DicOrderStatus


class DicOrderTypeRepo(BaseRepository):
    model = DicOrderType


class DicRiskDegreeRepo(BaseRepository):
    model = DicRiskDegree


class DicRiskNameRepo(BaseRepository):
    model = DicRiskName


class DicRiskTypeRepo(BaseRepository):
    model = DicRiskType


class RisksRepo(BaseRepository):
    model = Risks

    async def get_risks_with_details(self, filters: RisksFilterDto):
        try:
            query = (
                select(self.model)
                .join(
                    Organizations,
                    self.model.organization_id == Organizations.id,
                    isouter=True,
                )
                .join(DicRiskType, self.model.risk_type == DicRiskType.id, isouter=True)
                .join(DicRiskName, self.model.risk_name == DicRiskName.id, isouter=True)
                .join(
                    DicRiskDegree,
                    self.model.risk_degree == DicRiskDegree.id,
                    isouter=True,
                )
            )

            if filters.risk_degree_id is not None:
                query = query.filter(self.model.risk_degree == filters.risk_degree_id)

            if filters.risk_type_id is not None:
                query = query.filter(self.model.risk_type == filters.risk_type_id)

            if filters.risk_name_id is not None:
                query = query.filter(self.model.risk_name == filters.risk_name_id)

            if filters.iin_bin is not None:
                query = query.filter(Organizations.iin_bin == filters.iin_bin)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей рисков.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске рисков по фильтрам {filters}: {e}")
            raise
