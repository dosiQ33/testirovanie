from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import BaseRepository
from .models import Employees, DicUl, DicRoles, DicFl
from .dtos import EmployeesFilterDto


class DicUlRepo(BaseRepository):
    model = DicUl

    async def get_by_parent_id(self, parent_id: int) -> List[DicUl]:
        """Получить все дочерние организации по parent_id"""
        try:
            query = select(self.model).filter_by(parent_id=parent_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(
                f"Найдено {len(records)} дочерних организаций для parent_id={parent_id}"
            )
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске дочерних организаций для parent_id={parent_id}: {e}"
            )
            raise

    async def get_by_kato(self, kato: str) -> Optional[DicUl]:
        """Получить организацию по коду КАТО"""
        try:
            query = select(self.model).filter_by(kato=kato)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            logger.info(
                f"Организация с КАТО {kato} {'найдена' if record else 'не найдена'}"
            )
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске организации по КАТО {kato}: {e}")
            raise

    async def get_by_bin(self, bin_code: str) -> Optional[DicUl]:
        """Получить организацию по БИН"""
        try:
            query = select(self.model).filter_by(bin=bin_code)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            logger.info(
                f"Организация с БИН {bin_code} {'найдена' if record else 'не найдена'}"
            )
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске организации по БИН {bin_code}: {e}")
            raise


class DicRolesRepo(BaseRepository):
    model = DicRoles

    async def get_by_name(self, role_name: str) -> Optional[DicRoles]:
        """Получить роль по названию"""
        try:
            query = select(self.model).filter_by(role_name=role_name)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            logger.info(f"Роль {role_name} {'найдена' if record else 'не найдена'}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске роли {role_name}: {e}")
            raise


class DicFlRepo(BaseRepository):
    model = DicFl

    async def get_by_iin(self, iin: str) -> Optional[DicFl]:
        """Получить физическое лицо по ИИН"""
        try:
            query = select(self.model).filter_by(iin=iin)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            logger.info(
                f"Физическое лицо с ИИН {iin} {'найдено' if record else 'не найдено'}"
            )
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске физического лица по ИИН {iin}: {e}")
            raise

    async def search_by_name(
        self, surname: str = None, name: str = None
    ) -> List[DicFl]:
        """Поиск физических лиц по имени и фамилии"""
        try:
            query = select(self.model)

            if surname:
                query = query.filter(self.model.surname.ilike(f"%{surname}%"))

            if name:
                query = query.filter(self.model.name.ilike(f"%{name}%"))

            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} физических лиц по поиску")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске физических лиц: {e}")
            raise


class EmployeesRepo(BaseRepository):
    model = Employees

    async def filter_employees(self, filters: EmployeesFilterDto):
        """Get employees with custom filtering"""
        try:
            query = (
                select(self.model)
                .outerjoin(DicFl, self.model.fl_id == DicFl.id)
                .outerjoin(DicUl, self.model.ul_id == DicUl.id)
                .outerjoin(DicRoles, self.model.role == DicRoles.id)
            )

            if filters.id is not None:
                query = query.filter(self.model.id == filters.id)

            if filters.fl_id is not None:
                query = query.filter(self.model.fl_id == filters.fl_id)

            if filters.ul_id is not None:
                query = query.filter(self.model.ul_id == filters.ul_id)

            if filters.role_id is not None:
                query = query.filter(self.model.role == filters.role_id)

            if filters.login is not None:
                query = query.filter(self.model.login.ilike(f"%{filters.login}%"))

            if filters.deleted is not None:
                query = query.filter(self.model.deleted == filters.deleted)

            if filters.blocked is not None:
                query = query.filter(self.model.blocked == filters.blocked)

            if filters.employee_position is not None:
                query = query.filter(
                    self.model.employee_position.ilike(f"%{filters.employee_position}%")
                )

            if filters.employee_department is not None:
                query = query.filter(
                    self.model.employee_department.ilike(
                        f"%{filters.employee_department}%"
                    )
                )

            if filters.employee_status is not None:
                query = query.filter(
                    self.model.employee_status.ilike(f"%{filters.employee_status}%")
                )

            query = query.order_by(self.model.id.desc())

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} сотрудников.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников по фильтрам {filters}: {e}")
            raise

    async def get_many(
        self, filters=None, page_size: int | None = None, page: int | None = None
    ):
        """Override to handle joins for related entity filtering"""
        try:
            query = (
                select(self.model)
                .outerjoin(DicFl, self.model.fl_id == DicFl.id)
                .outerjoin(DicUl, self.model.ul_id == DicUl.id)
                .outerjoin(DicRoles, self.model.role == DicRoles.id)
            )

            count_query = (
                select(func.count(self.model.id))
                .outerjoin(DicFl, self.model.fl_id == DicFl.id)
                .outerjoin(DicUl, self.model.ul_id == DicUl.id)
                .outerjoin(DicRoles, self.model.role == DicRoles.id)
            )

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
            records = result.unique().scalars().all()

            logger.info(
                f"Найдено {len(records)} записей (page_size={page_size}, page={page}). Всего: {total}"
            )

            return records, total
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников: {e}")
            raise
