from sqlalchemy import select, func

from app.modules.common.repository import BaseExtRepository

from .models import (
    IucAlko,
    IucNeftebasaCoordinatesTemp,
    IucAzsCoordinatesTemp,
    IucNpzCoordinatesTemp,
    IucZernoCoordinatesTemp,
)
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

class IucAlkoRepository(BaseExtRepository):
    model = IucAlko

    async def get_info(self, activ_id: int): 
        try:
            query = (
                select(
                    IucAlko.name_ru,
                    IucAlko.iin_bin,
                    (IucAlko.region + ", " + IucAlko.district).label('address'),
                    IucAlko.organization_id
                )
                .select_from(
                    IucAlko
                )
                .where(
                    IucAlko.id == activ_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске данных о видах деятельности: {e}")
            raise

class IucNeftebasaRepository(BaseExtRepository):
    model = IucNeftebasaCoordinatesTemp

    async def get_info(self, activ_id: int): 
        try:
            query = (
                select(
                    IucNeftebasaCoordinatesTemp.object_name,
                    IucNeftebasaCoordinatesTemp.iin_bin,
                    (
                        IucNeftebasaCoordinatesTemp.region + ", " + IucNeftebasaCoordinatesTemp.district + ", " + IucNeftebasaCoordinatesTemp.address
                    ).label('address'),
                    IucNeftebasaCoordinatesTemp.organization_id
                )
                .select_from(
                    IucNeftebasaCoordinatesTemp
                )
                .where(
                    IucNeftebasaCoordinatesTemp.id == activ_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске данных о видах деятельности: {e}")
            raise

class IucAzsRepository(BaseExtRepository):
    model = IucAzsCoordinatesTemp

    async def get_info(self, activ_id: int): 
        try:
            query = (
                select(
                    IucAzsCoordinatesTemp.object_name,
                    IucAzsCoordinatesTemp.iin_bin,
                    (
                        IucAzsCoordinatesTemp.region + ", " + IucAzsCoordinatesTemp.district + ", " + IucAzsCoordinatesTemp.address
                    ).label('address'),
                    IucAzsCoordinatesTemp.organization_id
                )
                .select_from(
                    IucAzsCoordinatesTemp
                )
                .where(
                    IucAzsCoordinatesTemp.id == activ_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске данных о видах деятельности: {e}")
            raise 

class IucNpzRepository(BaseExtRepository):
    model = IucNpzCoordinatesTemp

    async def get_info(self, activ_id: int): 
        try:
            query = (
                select(
                    IucNpzCoordinatesTemp.object_name,
                    IucNpzCoordinatesTemp.iin_bin,
                    (
                        IucNpzCoordinatesTemp.region + ", " + IucNpzCoordinatesTemp.district + ", " + IucNpzCoordinatesTemp.address
                    ).label('address'),
                    IucNpzCoordinatesTemp.organization_id
                )
                .select_from(
                    IucNpzCoordinatesTemp
                )
                .where(
                    IucNpzCoordinatesTemp.id == activ_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске данных о видах деятельности: {e}")
            raise 

class IucZernoRepository(BaseExtRepository):
    model = IucZernoCoordinatesTemp

    async def get_info(self, activ_id: int): 
        try:
            query = (
                select(
                    IucZernoCoordinatesTemp.subject_name,
                    IucZernoCoordinatesTemp.iin_bin,
                    (
                        IucZernoCoordinatesTemp.region + ", " + IucZernoCoordinatesTemp.district + ", " + IucZernoCoordinatesTemp.address
                    ).label('address'),
                    IucZernoCoordinatesTemp.granary_capacity_tons,
                    IucZernoCoordinatesTemp.load_capacity_tons,
                    IucZernoCoordinatesTemp.organization_id
                )
                .select_from(
                    IucZernoCoordinatesTemp
                )
                .where(
                    IucZernoCoordinatesTemp.id == activ_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске данных о видах деятельности: {e}")
            raise 