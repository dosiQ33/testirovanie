from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl
from .dtos import EmployeesDto, DicUlDto, DicRolesDto, DicFlDto, EmployeesFilterDto
from .models import Employees, DicUl, DicRoles, DicFl
from .repository import EmployeesRepo, DicUlRepo, DicRolesRepo, DicFlRepo
from .filters import EmployeesFilter, DicUlFilter, DicRolesFilter, DicFlFilter

router = APIRouter(prefix="/admins")

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


class EmployeesRouter(APIRouter):
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
        Get employees with custom filtering

        - **id**: Employee ID
        - **fl_id**: Physical person ID
        - **ul_id**: Organization ID
        - **role_id**: Role ID
        - **login**: Login (partial match)
        - **deleted**: Deleted status
        - **blocked**: Blocked status
        - **employee_position**: Position (partial match)
        - **employee_department**: Department (partial match)
        - **employee_status**: Status (partial match)
        """
        response = await EmployeesRepo(session).filter_employees(filters)
        return [EmployeesDto.model_validate(item) for item in response]


router.include_router(dic_ul_router)
router.include_router(dic_roles_router)
router.include_router(dic_fl_router)
router.include_router(EmployeesRouter())
