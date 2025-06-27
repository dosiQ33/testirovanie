"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from sqlalchemy import select
from app.modules.common.repository import BaseExtRepository
from .models import KazgeodesyRkOblasti, KazgeodesyRkRaiony
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError


class KazgeodesyRkOblastiRepo(BaseExtRepository):
    model = KazgeodesyRkOblasti

    async def get_geom(self, id: int):
        try:
            query = select(self.model).filter_by(id=id)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {id}: {e}")
            raise


class KazgeodesyRkRaionyRepo(BaseExtRepository):
    model = KazgeodesyRkRaiony

    async def get_geom(self, id: int):
        try:
            query = select(self.model).filter_by(id=id)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {id}: {e}")
            raise
