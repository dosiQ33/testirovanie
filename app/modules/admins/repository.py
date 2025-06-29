from app.modules.common.repository import BaseRepository
from .models import Employees, DicUl, DicRoles, DicFl


class DicUlRepo(BaseRepository):
    model = DicUl


class DicRolesRepo(BaseRepository):
    model = DicRoles


class DicFlRepo(BaseRepository):
    model = DicFl


class EmployeesRepo(BaseRepository):
    model = Employees
