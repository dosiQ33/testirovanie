from typing import Annotated, List, Optional
from fastapi import APIRouter, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from fastapi_cache.decorator import cache
from loguru import logger

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl
from .dtos import (
    EmployeeInfoDto,
    EmployeesDto,
    DicUlDto,
    DicRolesDto,
    DicFlDto,
    EmployeesFilterDto,
    DicFlCreateDto,
    DicFlUpdateDto,
    DicUlCreateDto,
    DicUlUpdateDto,
    EmployeesCreateDto,
    EmployeesUpdateDto,
)
from .models import Employees, DicUl, DicRoles, DicFl
from .repository import EmployeesRepo, DicUlRepo, DicRolesRepo, DicFlRepo
from .filters import EmployeesFilter, DicUlFilter, DicRolesFilter, DicFlFilter
from app.modules.admins.deps import get_current_employee
from app.modules.admins.auth import router as auth_router

router = APIRouter(prefix="/admins", tags=["Admin Panel"])

dic_roles_router = BaseCRUDRouter(
    "dic-roles",
    DicRoles,
    DicRolesRepo,
    DicRolesDto,
    DicRolesFilter,
    tags=["admins: dic-roles"],
)


class DicFlRouter(APIRouter):
    """Роутер для справочника физических лиц с полным CRUD"""

    sub_router = APIRouter(prefix="/dic-fl", tags=["admins: dic-fl"])
    base_router = BaseCRUDRouter(
        "dic-fl", DicFl, DicFlRepo, DicFlDto, DicFlFilter, tags=["admins: dic-fl"]
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", response_model=List[DicFlDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_dic_fl(
        iin: Optional[str] = Query(None, description="Фильтр по ИИН"),
        surname: Optional[str] = Query(None, description="Фильтр по фамилии"),
        name: Optional[str] = Query(None, description="Фильтр по имени"),
        page: Optional[int] = Query(None, description="Номер страницы"),
        page_size: Optional[int] = Query(None, description="Размер страницы"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Фильтрация физических лиц с поддержкой пагинации

        - **iin**: ИИН (частичное совпадение)
        - **surname**: фамилия (частичное совпадение)
        - **name**: имя (частичное совпадение)
        - **page**: номер страницы
        - **page_size**: количество записей на странице
        """
        try:
            query = select(DicFl)

            if iin:
                query = query.filter(DicFl.iin.ilike(f"%{iin}%"))
            if surname:
                query = query.filter(DicFl.surname.ilike(f"%{surname}%"))
            if name:
                query = query.filter(DicFl.name.ilike(f"%{name}%"))

            query = query.order_by(DicFl.id.desc())

            if page_size and page:
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)
            elif page_size:
                query = query.limit(page_size)

            result = await session.execute(query)
            records = result.unique().scalars().all()

            return [DicFlDto.model_validate(item) for item in records]
        except Exception as e:
            logger.error(f"Ошибка при фильтрации dic_fl: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при поиске записей")

    @sub_router.post("", response_model=DicFlDto, status_code=status.HTTP_201_CREATED)
    async def create_dic_fl(
        data: DicFlCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Создать новое физическое лицо

        - **iin**: ИИН
        - **surname**: фамилия
        - **name**: имя
        - **patronymic**: отчество
        - **date_of_birth**: дата рождения
        - **email**: электронная почта
        - **phone**: телефон
        - **create_date**: дата создания
        """
        if data.iin:
            existing = await DicFlRepo(session).get_by_iin(data.iin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Физическое лицо с ИИН {data.iin} уже существует",
                )

        new_record = await DicFlRepo(session).create(data)
        return DicFlDto.model_validate(new_record)

    @sub_router.put("/{id}", response_model=DicFlDto)
    async def update_dic_fl(
        id: int,
        data: DicFlUpdateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Обновить физическое лицо по ID

        - **id**: ID физического лица
        - **iin**: ИИН
        - **surname**: фамилия
        - **name**: имя
        - **patronymic**: отчество
        - **date_of_birth**: дата рождения
        - **email**: электронная почта
        - **phone**: телефон
        """
        if data.iin:
            existing = await DicFlRepo(session).get_by_iin(data.iin)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Физическое лицо с ИИН {data.iin} уже существует",
                )

        updated_record = await DicFlRepo(session).update_by_id(id, data)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Физическое лицо не найдено",
            )
        return DicFlDto.model_validate(updated_record)

    @sub_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_dic_fl(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Удалить физическое лицо по ID

        - **id**: ID физического лица
        """
        deleted = await DicFlRepo(session).delete_by_id(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Физическое лицо не найдено",
            )


class DicUlRouter(APIRouter):
    """Роутер для справочника юридических лиц с полным CRUD"""

    sub_router = APIRouter(prefix="/dic-ul", tags=["admins: dic-ul"])
    base_router = BaseCRUDRouter(
        "dic-ul", DicUl, DicUlRepo, DicUlDto, DicUlFilter, tags=["admins: dic-ul"]
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", response_model=List[DicUlDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_dic_ul(
        bin: Optional[str] = Query(None, description="Фильтр по БИН"),
        name: Optional[str] = Query(None, description="Фильтр по наименованию"),
        shortname: Optional[str] = Query(
            None, description="Фильтр по краткому наименованию"
        ),
        page: Optional[int] = Query(None, description="Номер страницы"),
        page_size: Optional[int] = Query(None, description="Размер страницы"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Фильтрация юридических лиц с поддержкой пагинации

        - **bin**: БИН (частичное совпадение)
        - **name**: наименование (частичное совпадение)
        - **shortname**: краткое наименование (частичное совпадение)
        - **page**: номер страницы
        - **page_size**: количество записей на странице
        """
        try:
            query = select(DicUl)

            if bin:
                query = query.filter(DicUl.bin.ilike(f"%{bin}%"))
            if name:
                query = query.filter(DicUl.name.ilike(f"%{name}%"))
            if shortname:
                query = query.filter(DicUl.shortname.ilike(f"%{shortname}%"))

            query = query.order_by(DicUl.id.desc())

            if page_size and page:
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)
            elif page_size:
                query = query.limit(page_size)

            result = await session.execute(query)
            records = result.unique().scalars().all()

            return [DicUlDto.model_validate(item) for item in records]
        except Exception as e:
            logger.error(f"Ошибка при фильтрации dic_ul: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при поиске записей")

    @sub_router.post("", response_model=DicUlDto, status_code=status.HTTP_201_CREATED)
    async def create_dic_ul(
        data: DicUlCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Создать новое юридическое лицо

        - **parent_id**: ID родительской организации
        - **bin**: БИН
        - **shortname**: краткое наименование
        - **name**: полное наименование
        - **address**: адрес
        - **kato**: код КАТО
        - **oblast_id**: ID области
        - **raion_id**: ID района
        - **create_date**: дата создания
        """
        if data.bin:
            existing = await DicUlRepo(session).get_by_bin(data.bin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Юридическое лицо с БИН {data.bin} уже существует",
                )

        new_record = await DicUlRepo(session).create(data)
        return DicUlDto.model_validate(new_record)

    @sub_router.put("/{id}", response_model=DicUlDto)
    async def update_dic_ul(
        id: int,
        data: DicUlUpdateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Обновить юридическое лицо по ID

        - **id**: ID юридического лица
        - **parent_id**: ID родительской организации
        - **bin**: БИН
        - **shortname**: краткое наименование
        - **name**: полное наименование
        - **address**: адрес
        - **kato**: код КАТО
        - **oblast_id**: ID области
        - **raion_id**: ID района
        """
        if data.bin:
            existing = await DicUlRepo(session).get_by_bin(data.bin)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Юридическое лицо с БИН {data.bin} уже существует",
                )

        updated_record = await DicUlRepo(session).update_by_id(id, data)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Юридическое лицо не найдено",
            )
        return DicUlDto.model_validate(updated_record)

    @sub_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_dic_ul(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Удалить юридическое лицо по ID

        - **id**: ID юридического лица
        """
        deleted = await DicUlRepo(session).delete_by_id(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Юридическое лицо не найдено",
            )


class EmployeesRouter(APIRouter):
    """Роутер для сотрудников с полным CRUD"""

    sub_router = APIRouter(prefix="/employees", tags=["admins: employees"])
    base_router = BaseCRUDRouter(
        "employees",
        Employees,
        EmployeesRepo,
        EmployeesDto,
        EmployeesFilter,
        tags=["admins: employees"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_employees(
        filters: Annotated[EmployeesFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[EmployeesDto]:
        """
        Получить сотрудников с расширенной фильтрацией

        - **id**: ID сотрудника
        - **fl_id**: ID физического лица
        - **ul_id**: ID организации
        - **role_id**: ID роли
        - **login**: логин (частичное совпадение)
        - **deleted**: статус удаления
        - **blocked**: статус блокировки
        - **employee_position**: должность (частичное совпадение)
        - **employee_department**: отдел (частичное совпадение)
        - **employee_status**: статус сотрудника (частичное совпадение)
        - **empl_create_date_from**: дата создания сотрудника с
        - **empl_create_date_to**: дата создания сотрудника по
        - **fl_surname**: фамилия физического лица (частичное совпадение)
        - **fl_name**: имя физического лица (частичное совпадение)
        - **fl_iin**: ИИН физического лица (частичное совпадение)
        - **ul_name**: название организации (частичное совпадение)
        - **ul_bin**: БИН организации (частичное совпадение)
        """
        response = await EmployeesRepo(session).filter_employees(filters)
        return [EmployeesDto.model_validate(item) for item in response]

    @sub_router.post(
        "", response_model=EmployeesDto, status_code=status.HTTP_201_CREATED
    )
    async def create_employee(
        data: EmployeesCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Создать нового сотрудника

        - **fl_id**: ID физического лица
        - **ul_id**: ID организации
        - **role**: ID роли
        - **login**: логин
        - **password**: пароль
        - **deleted**: статус удаления
        - **blocked**: статус блокировки
        - **empl_create_date**: дата создания сотрудника
        - **employee_position**: должность
        - **employee_department**: отдел
        - **employee_status**: статус сотрудника
        """
        if data.login:
            existing_employees = await EmployeesRepo(session).filter_employees(
                EmployeesFilterDto(login=data.login)
            )
            if existing_employees:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Сотрудник с логином {data.login} уже существует",
                )

        if data.fl_id:
            fl = await DicFlRepo(session).get_one_by_id(data.fl_id)
            if not fl:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Физическое лицо с ID {data.fl_id} не найдено",
                )

        if data.ul_id:
            ul = await DicUlRepo(session).get_one_by_id(data.ul_id)
            if not ul:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Организация с ID {data.ul_id} не найдена",
                )

        if data.role:
            role = await DicRolesRepo(session).get_one_by_id(data.role)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Роль с ID {data.role} не найдена",
                )

        new_record = await EmployeesRepo(session).create(data)
        return EmployeesDto.model_validate(new_record)

    @sub_router.put("/{id}", response_model=EmployeesDto)
    async def update_employee(
        id: int,
        data: EmployeesUpdateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Обновить сотрудника по ID

        - **id**: ID сотрудника
        - **fl_id**: ID физического лица
        - **ul_id**: ID организации
        - **role**: ID роли
        - **login**: логин
        - **password**: пароль
        - **deleted**: статус удаления
        - **blocked**: статус блокировки
        - **employee_position**: должность
        - **employee_department**: отдел
        - **employee_status**: статус сотрудника
        """
        if data.login:
            existing_employees = await EmployeesRepo(session).filter_employees(
                EmployeesFilterDto(login=data.login)
            )
            if existing_employees and existing_employees[0].id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Сотрудник с логином {data.login} уже существует",
                )

        if data.fl_id:
            fl = await DicFlRepo(session).get_one_by_id(data.fl_id)
            if not fl:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Физическое лицо с ID {data.fl_id} не найдено",
                )

        if data.ul_id:
            ul = await DicUlRepo(session).get_one_by_id(data.ul_id)
            if not ul:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Организация с ID {data.ul_id} не найдена",
                )

        if data.role:
            role = await DicRolesRepo(session).get_one_by_id(data.role)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Роль с ID {data.role} не найдена",
                )

        updated_record = await EmployeesRepo(session).update_by_id(id, data)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
            )
        return EmployeesDto.model_validate(updated_record)

    @sub_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_employee(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """
        Удалить сотрудника по ID

        - **id**: ID сотрудника
        """
        deleted = await EmployeesRepo(session).delete_by_id(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
            )


@router.get("/me", response_model=EmployeeInfoDto)
async def get_current_employee_info(
    current_employee: Employees = Depends(get_current_employee),
) -> EmployeeInfoDto:
    """Получить информацию о текущем авторизованном сотруднике"""
    return EmployeeInfoDto.model_validate(current_employee)


router.include_router(auth_router)
router.include_router(dic_roles_router)
router.include_router(DicFlRouter())
router.include_router(DicUlRouter())
router.include_router(EmployeesRouter())
