from fastapi import APIRouter

from app.modules.common.router import BaseCRUDRouter
from .dtos import EmployeesDto, DicUlDto, DicRolesDto, DicFlDto
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

employees_router = BaseCRUDRouter(
    "employees",
    Employees,
    EmployeesRepo,
    EmployeesDto,
    EmployeesFilter,
    tags=["admins: employees"],
)

router.include_router(dic_ul_router)
router.include_router(dic_roles_router)
router.include_router(dic_fl_router)
router.include_router(employees_router)
