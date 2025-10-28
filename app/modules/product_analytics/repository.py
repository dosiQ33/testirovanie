from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import BaseRepository
from .models import GtinNp, GtinKkms
from .dtos import GtinNpFilterDto, GtinKkmsFilterDto


class GtinNpRepo(BaseRepository):
    """Репозиторий для GTIN по налогоплательщикам"""

    model = GtinNp

    async def filter(self, filters: GtinNpFilterDto) -> List[GtinNp]:
        """Фильтрация GTIN по налогоплательщикам"""
        try:
            query = select(self.model)

            if filters.dtype is not None:
                query = query.filter(GtinNp.dtype == filters.dtype)

            if filters.org_id is not None:
                query = query.filter(GtinNp.org_id == filters.org_id)

            if filters.gtin is not None:
                query = query.filter(GtinNp.gtin == filters.gtin)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей GTIN по НП.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при фильтрации GTIN по НП: {e}")
            raise

    async def get_by_organization_id(self, org_id: int) -> List[GtinNp]:
        """Получить все GTIN для организации"""
        try:
            query = select(self.model).filter(GtinNp.org_id == org_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} GTIN для организации {org_id}.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении GTIN для организации: {e}")
            raise


class GtinKkmsRepo(BaseRepository):
    """Репозиторий для GTIN по ККМ"""

    model = GtinKkms

    async def filter(self, filters: GtinKkmsFilterDto) -> List[GtinKkms]:
        """Фильтрация GTIN по ККМ"""
        try:
            query = select(self.model)

            if filters.dtype is not None:
                query = query.filter(GtinKkms.dtype == filters.dtype)

            if filters.kkms_id is not None:
                query = query.filter(GtinKkms.kkms_id == filters.kkms_id)

            if filters.gtin is not None:
                query = query.filter(GtinKkms.gtin == filters.gtin)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей GTIN по ККМ.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при фильтрации GTIN по ККМ: {e}")
            raise

    async def get_by_kkm_id(self, kkms_id: int) -> List[GtinKkms]:
        """Получить все GTIN для ККМ"""
        try:
            query = select(self.model).filter(GtinKkms.kkms_id == kkms_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} GTIN для ККМ {kkms_id}.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении GTIN для ККМ: {e}")
            raise
