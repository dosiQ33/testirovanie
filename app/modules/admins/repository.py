from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import BaseRepository
from .models import Employees, DicUl, DicRoles, DicFl


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

    async def get_many(
        self, filters=None, page_size: int | None = None, page: int | None = None
    ):
        """Override to handle joins for related entity filtering"""
        try:
            # Base query with joins for related entities
            query = (
                select(self.model)
                .outerjoin(DicFl, self.model.fl_id == DicFl.id)
                .outerjoin(DicUl, self.model.ul_id == DicUl.id)
                .outerjoin(DicRoles, self.model.role == DicRoles.id)
            )

            # Count query with same joins
            count_query = (
                select(func.count(self.model.id))
                .outerjoin(DicFl, self.model.fl_id == DicFl.id)
                .outerjoin(DicUl, self.model.ul_id == DicUl.id)
                .outerjoin(DicRoles, self.model.role == DicRoles.id)
            )

            # Apply filters if provided
            if filters is not None:
                query = filters.filter(query)
                count_query = filters.filter(count_query)

            # Get total count
            total = (await self._session.execute(count_query)).scalar()

            # Apply pagination
            if page_size is not None and page is not None:
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)
            elif page_size is not None:
                query = query.limit(page_size)

            # Execute query
            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(
                f"Найдено {len(records)} записей (page_size={page_size}, page={page}). Всего: {total}"
            )

            return records, total
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников: {e}")
            raise

    async def get_by_login(self, login: str) -> Optional[Employees]:
        """Получить сотрудника по логину"""
        try:
            query = select(self.model).filter_by(login=login)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            logger.info(
                f"Сотрудник с логином {login} {'найден' if record else 'не найден'}"
            )
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудника по логину {login}: {e}")
            raise

    async def get_by_ul_id(self, ul_id: int) -> List[Employees]:
        """Получить всех сотрудников организации"""
        try:
            query = select(self.model).filter_by(ul_id=ul_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(
                f"Найдено {len(records)} сотрудников для организации ul_id={ul_id}"
            )
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников для ul_id={ul_id}: {e}")
            raise

    async def get_by_role(self, role_id: int) -> List[Employees]:
        """Получить всех сотрудников с определенной ролью"""
        try:
            query = select(self.model).filter_by(role=role_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} сотрудников с ролью role={role_id}")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников с ролью role={role_id}: {e}")
            raise

    async def get_active_employees(self) -> List[Employees]:
        """Получить всех активных (не удаленных и не заблокированных) сотрудников"""
        try:
            query = select(self.model).filter(
                (self.model.deleted.is_(False) | self.model.deleted.is_(None))
                & (self.model.blocked.is_(False) | self.model.blocked.is_(None))
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} активных сотрудников")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске активных сотрудников: {e}")
            raise

    async def get_by_department(self, department: str) -> List[Employees]:
        """Получить всех сотрудников отдела"""
        try:
            query = select(self.model).filter_by(employee_department=department)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} сотрудников в отделе {department}")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников отдела {department}: {e}")
            raise

    async def get_by_position(self, position: str) -> List[Employees]:
        """Получить всех сотрудников с определенной должностью"""
        try:
            query = select(self.model).filter_by(employee_position=position)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} сотрудников с должностью {position}")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников с должностью {position}: {e}")
            raise

    async def search_by_organization_name(self, org_name: str) -> List[Employees]:
        """Поиск сотрудников по названию организации"""
        try:
            query = (
                select(self.model)
                .join(DicUl, self.model.ul_id == DicUl.id)
                .filter(DicUl.name.ilike(f"%{org_name}%"))
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(
                f"Найдено {len(records)} сотрудников по названию организации '{org_name}'"
            )
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников по названию организации: {e}")
            raise

    async def search_by_role_name(self, role_name: str) -> List[Employees]:
        """Поиск сотрудников по названию роли"""
        try:
            query = (
                select(self.model)
                .join(DicRoles, self.model.role == DicRoles.id)
                .filter(DicRoles.role_name.ilike(f"%{role_name}%"))
            )
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} сотрудников с ролью '{role_name}'")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников по роли: {e}")
            raise

    async def search_by_person_name(
        self, surname: str = None, name: str = None
    ) -> List[Employees]:
        """Поиск сотрудников по имени/фамилии физического лица"""
        try:
            query = select(self.model).join(DicFl, self.model.fl_id == DicFl.id)

            if surname:
                query = query.filter(DicFl.surname.ilike(f"%{surname}%"))

            if name:
                query = query.filter(DicFl.name.ilike(f"%{name}%"))

            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(f"Найдено {len(records)} сотрудников по имени/фамилии")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске сотрудников по имени: {e}")
            raise
