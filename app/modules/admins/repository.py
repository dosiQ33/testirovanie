from typing import List, Optional
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import BaseRepository
from .models import DicIndicators, EmployeeIndicators, Employees, DicUl, DicRoles, DicFl
from .dtos import (
    EmployeesFilterDto,
    DicFlCreateDto,
    DicFlUpdateDto,
    DicUlCreateDto,
    DicUlUpdateDto,
    EmployeesCreateDto,
    EmployeesUpdateDto,
)


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

    async def create(self, data: DicUlCreateDto) -> DicUl:
        """Создать новую организацию"""
        try:
            new_record = self.model(**data.model_dump(exclude_unset=True))
            self._session.add(new_record)
            await self._session.flush()
            await self._session.refresh(new_record)
            logger.info(f"Создана новая организация с ID {new_record.id}")
            return new_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании организации: {e}")
            raise

    async def update_by_id(self, id: int, data: DicUlUpdateDto) -> Optional[DicUl]:
        """Обновить организацию по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return None

            update_data = data.model_dump(exclude_unset=True)
            if update_data:
                stmt = (
                    update(self.model).where(self.model.id == id).values(**update_data)
                )
                await self._session.execute(stmt)
                await self._session.flush()

                updated_record = await self.get_one_by_id(id)
                logger.info(f"Обновлена организация с ID {id}")
                return updated_record

            return existing_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении организации с ID {id}: {e}")
            raise

    async def delete_by_id(self, id: int) -> bool:
        """Удалить организацию по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return False

            stmt = delete(self.model).where(self.model.id == id)
            result = await self._session.execute(stmt)
            await self._session.flush()

            logger.info(f"Удалена организация с ID {id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении организации с ID {id}: {e}")
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

    async def create(self, data: DicFlCreateDto) -> DicFl:
        """Создать новое физическое лицо"""
        try:
            new_record = self.model(**data.model_dump(exclude_unset=True))
            self._session.add(new_record)
            await self._session.flush()
            await self._session.refresh(new_record)
            logger.info(f"Создано новое физическое лицо с ID {new_record.id}")
            return new_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании физического лица: {e}")
            raise

    async def update_by_id(self, id: int, data: DicFlUpdateDto) -> Optional[DicFl]:
        """Обновить физическое лицо по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return None

            update_data = data.model_dump(exclude_unset=True)
            if update_data:
                stmt = (
                    update(self.model).where(self.model.id == id).values(**update_data)
                )
                await self._session.execute(stmt)
                await self._session.flush()

                updated_record = await self.get_one_by_id(id)
                logger.info(f"Обновлено физическое лицо с ID {id}")
                return updated_record

            return existing_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении физического лица с ID {id}: {e}")
            raise

    async def delete_by_id(self, id: int) -> bool:
        """Удалить физическое лицо по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return False

            stmt = delete(self.model).where(self.model.id == id)
            result = await self._session.execute(stmt)
            await self._session.flush()

            logger.info(f"Удалено физическое лицо с ID {id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении физического лица с ID {id}: {e}")
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

            if filters.empl_create_date_from is not None:
                query = query.filter(
                    self.model.empl_create_date >= filters.empl_create_date_from
                )

            if filters.empl_create_date_to is not None:
                query = query.filter(
                    self.model.empl_create_date <= filters.empl_create_date_to
                )

            if filters.fl_surname is not None:
                query = query.filter(DicFl.surname.ilike(f"%{filters.fl_surname}%"))

            if filters.fl_name is not None:
                query = query.filter(DicFl.name.ilike(f"%{filters.fl_name}%"))

            if filters.fl_iin is not None:
                query = query.filter(DicFl.iin.ilike(f"%{filters.fl_iin}%"))

            if filters.ul_name is not None:
                query = query.filter(DicUl.name.ilike(f"%{filters.ul_name}%"))

            if filters.ul_bin is not None:
                query = query.filter(DicUl.bin.ilike(f"%{filters.ul_bin}%"))

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

    async def create(
        self, data: EmployeesCreateDto, assigned_by: Optional[int] = None
    ) -> Employees:
        """Создать нового сотрудника"""
        try:
            indicator_ids = data.indicator_ids
            employee_data = data.model_dump(
                exclude_unset=True, exclude={"indicator_ids"}
            )

            new_record = self.model(**employee_data)
            self._session.add(new_record)
            await self._session.flush()
            await self._session.refresh(new_record)

            if indicator_ids:
                indicators_repo = EmployeeIndicatorsRepo(self._session)
                await indicators_repo.add_indicators_to_employee(
                    new_record.id, indicator_ids
                )
                await self._session.refresh(new_record)

            logger.info(f"Создан новый сотрудник с ID {new_record.id}")
            return new_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании сотрудника: {e}")
            raise

    async def update_by_id(
        self, id: int, data: EmployeesUpdateDto, assigned_by: Optional[int] = None
    ) -> Optional[Employees]:
        """Обновить сотрудника по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return None

            indicator_ids = data.indicator_ids
            update_data = data.model_dump(exclude_unset=True, exclude={"indicator_ids"})

            if update_data:
                stmt = (
                    update(self.model).where(self.model.id == id).values(**update_data)
                )
                await self._session.execute(stmt)
                await self._session.flush()

            if indicator_ids is not None:
                indicators_repo = EmployeeIndicatorsRepo(self._session)
                await indicators_repo.delete_by_employee_id(id)
                if indicator_ids:
                    await indicators_repo.add_indicators_to_employee(id, indicator_ids)

            updated_record = await self.get_one_by_id(id)
            logger.info(f"Обновлен сотрудник с ID {id}")
            return updated_record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении сотрудника с ID {id}: {e}")
            raise

    async def delete_by_id(self, id: int) -> bool:
        """Удалить сотрудника по ID"""
        try:
            existing_record = await self.get_one_by_id(id)
            if not existing_record:
                return False

            stmt = delete(self.model).where(self.model.id == id)
            result = await self._session.execute(stmt)
            await self._session.flush()

            logger.info(f"Удален сотрудник с ID {id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении сотрудника с ID {id}: {e}")
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


class DicIndicatorsRepo(BaseRepository):
    model = DicIndicators


class EmployeeIndicatorsRepo(BaseRepository):
    model = EmployeeIndicators

    async def get_by_employee_id(self, employee_id: int) -> List[EmployeeIndicators]:
        """Получить все показатели сотрудника"""
        try:
            query = select(self.model).filter_by(employee_id=employee_id)
            result = await self._session.execute(query)
            records = result.unique().scalars().all()
            logger.info(
                f"Найдено {len(records)} показателей для сотрудника {employee_id}"
            )
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске показателей сотрудника {employee_id}: {e}")
            raise

    async def delete_by_employee_id(self, employee_id: int) -> bool:
        """Удалить все показатели сотрудника"""
        try:
            stmt = delete(self.model).where(self.model.employee_id == employee_id)
            result = await self._session.execute(stmt)
            await self._session.flush()
            logger.info(f"Удалены показатели сотрудника {employee_id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при удалении показателей сотрудника {employee_id}: {e}"
            )
            raise

    async def add_indicators_to_employee(
        self, employee_id: int, indicator_ids: List[int]
    ) -> List[EmployeeIndicators]:
        """Добавить показатели к сотруднику"""
        try:
            new_indicators = []
            for indicator_id in indicator_ids:
                indicator = self.model(
                    employee_id=employee_id,
                    indicator_id=indicator_id,
                )
                new_indicators.append(indicator)

            self._session.add_all(new_indicators)
            await self._session.flush()

            logger.info(
                f"Добавлено {len(new_indicators)} показателей к сотруднику {employee_id}"
            )
            return new_indicators
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при добавлении показателей к сотруднику {employee_id}: {e}"
            )
            raise
