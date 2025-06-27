from typing import List, TypeVar, Generic, Type
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def get_one_by_id(self, id: int):
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

    async def get_one(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    async def get_many(self, filters=None, page_size: int | None = None, page: int | None = None):
        try:
            query = select(self.model)
            count_query = select(func.count(self.model.id))

            if filters is not None:
                query = filters.filter(query)
                count_query = filters.filter(count_query)
            total = (await self._session.execute(count_query)).scalar()

            if page_size is not None and page is not None:
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)
            elif page_size is not None:
                query = query.limit(page_size)

            result = await self._session.execute(query)
            records = result.scalars().all()

            logger.info(f"Найдено {len(records)} записей (page_size={page_size}, page={page}). Всего: {total}")

            return records, total
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def add(self, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Добавление записи {self.model.__name__} с параметрами: {values_dict}")
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            logger.info(f"Запись {self.model.__name__} успешно добавлена.")
            await self._session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise

    async def add_many(self, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Добавление нескольких записей {self.model.__name__}. Количество: {len(values_list)}")
        try:
            new_instances = [self.model(**values) for values in values_list]
            self._session.add_all(new_instances)
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
            await self._session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise

    async def update(self, filters: BaseModel, values: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Обновление записей {self.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            logger.info(f"Обновлено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    async def delete(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    async def count(self, filters=None):
        try:
            count_query = select(func.count(self.model.id))

            if filters is not None:
                count_query = filters.filter(count_query)
            count = (await self._session.execute(count_query)).scalar()

            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def bulk_update(self, records: List[BaseModel]):
        logger.info(f"Массовое обновление записей {self.model.__name__}")
        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump(exclude_unset=True)
                if "id" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "id"}
                stmt = sqlalchemy_update(self.model).filter_by(id=record_dict["id"]).values(**update_data)
                result = await self._session.execute(stmt)
                updated_count += result.rowcount

            logger.info(f"Обновлено {updated_count} записей")
            await self._session.flush()
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении: {e}")
            raise


class BaseWithOrganizationRepository(BaseRepository):
    async def get_by_organization_id(self, id: int):
        try:
            query = select(self.model).filter_by(organization_id=id)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            # logger.info(f"Найдено {len(record)} записей.")

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по organization_id {id}: {e}")
            raise


class BaseWithKkmRepository(BaseRepository):
    async def get_by_kkm_id(self, id: int):
        try:
            query = select(self.model).filter_by(kkm_id=id)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()

            # logger.info(f"Найдено {len(record)} записей.")

            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по kkm_id {id}: {e}")
            raise


class BaseExtRepository(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def get_one(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    async def get_many(self):
        try:
            query = select(self.model)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей: {e}")
            raise

    async def get_one_by_id(self, id: int):
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

    async def get_by_parent_id(self, parent_id: int):
        try:
            query = select(self.model).filter_by(parent_id=parent_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по parent_id {parent_id}: {e}")
            raise
