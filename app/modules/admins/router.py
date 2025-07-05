from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import List, Optional

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter
from .dtos import (
    EmployeesDto,
    DicUlDto,
    DicRolesDto,
    DicFlDto,
    EmployeesCreateDto,
    DicUlCreateDto,
    DicRolesCreateDto,
    DicFlCreateDto,
)
from .models import Employees, DicUl, DicRoles, DicFl
from .repository import EmployeesRepo, DicUlRepo, DicRolesRepo, DicFlRepo
from .filters import EmployeesFilter, DicUlFilter, DicRolesFilter, DicFlFilter


router = APIRouter(prefix="/admins")

# Dictionary routers with basic CRUD operations
dic_ul_router = BaseCRUDRouter(
    "dic-ul", DicUl, DicUlRepo, DicUlDto, DicUlFilter, tags=["admins: dic-ul"]
)

dic_roles_router = BaseCRUDRouter(
    "dic-roles",
    DicRoles,
    DicRolesRepo,
    DicRolesDto,
    DicRolesFilter,
    tags=["admins: dic-roles"],
)

dic_fl_router = BaseCRUDRouter(
    "dic-fl", DicFl, DicFlRepo, DicFlDto, DicFlFilter, tags=["admins: dic-fl"]
)


# Enhanced Employees Router with advanced filtering
class EmployeesRouter(APIRouter):
    """Enhanced Employees router with filtering by ul, fl, and role_ref"""

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

    @sub_router.post("/", response_model=EmployeesDto)
    async def create_employee(
        data: EmployeesCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """Создать нового сотрудника"""
        new_employee = await EmployeesRepo(session).add(data)
        return EmployeesDto.model_validate(new_employee)

    @sub_router.get("/by-organization/{ul_id}", response_model=List[EmployeesDto])
    async def get_employees_by_organization(
        ul_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        """Получить всех сотрудников организации по ID организации"""
        employees = await EmployeesRepo(session).get_by_ul_id(ul_id)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/by-role/{role_id}", response_model=List[EmployeesDto])
    async def get_employees_by_role(
        role_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        """Получить всех сотрудников с определенной ролью"""
        employees = await EmployeesRepo(session).get_by_role(role_id)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/active", response_model=List[EmployeesDto])
    async def get_active_employees(
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """Получить всех активных сотрудников (не удаленных и не заблокированных)"""
        employees = await EmployeesRepo(session).get_active_employees()
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/by-department/{department}", response_model=List[EmployeesDto])
    async def get_employees_by_department(
        department: str, session: AsyncSession = Depends(get_session_with_commit)
    ):
        """Получить всех сотрудников отдела"""
        employees = await EmployeesRepo(session).get_by_department(department)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/by-position/{position}", response_model=List[EmployeesDto])
    async def get_employees_by_position(
        position: str, session: AsyncSession = Depends(get_session_with_commit)
    ):
        """Получить всех сотрудников с определенной должностью"""
        employees = await EmployeesRepo(session).get_by_position(position)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/search/by-organization-name", response_model=List[EmployeesDto])
    async def search_employees_by_organization_name(
        org_name: str = Query(..., description="Название организации для поиска"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """Поиск сотрудников по названию организации"""
        employees = await EmployeesRepo(session).search_by_organization_name(org_name)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/search/by-role-name", response_model=List[EmployeesDto])
    async def search_employees_by_role_name(
        role_name: str = Query(..., description="Название роли для поиска"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """Поиск сотрудников по названию роли"""
        employees = await EmployeesRepo(session).search_by_role_name(role_name)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/search/by-person-name", response_model=List[EmployeesDto])
    async def search_employees_by_person_name(
        surname: Optional[str] = Query(None, description="Фамилия для поиска"),
        name: Optional[str] = Query(None, description="Имя для поиска"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        """Поиск сотрудников по имени/фамилии физического лица"""
        if not surname and not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Необходимо указать фамилию или имя для поиска",
            )

        employees = await EmployeesRepo(session).search_by_person_name(surname, name)
        return [EmployeesDto.model_validate(emp) for emp in employees]

    @sub_router.get("/login/{login}", response_model=EmployeesDto)
    async def get_employee_by_login(
        login: str, session: AsyncSession = Depends(get_session_with_commit)
    ):
        """Получить сотрудника по логину"""
        employee = await EmployeesRepo(session).get_by_login(login)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник с указанным логином не найден",
            )
        return EmployeesDto.model_validate(employee)


# Include all routers
router.include_router(dic_ul_router)
router.include_router(dic_roles_router)
router.include_router(dic_fl_router)
router.include_router(EmployeesRouter())
