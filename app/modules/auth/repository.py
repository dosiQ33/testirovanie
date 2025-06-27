from app.modules.common.repository import BaseRepository
from app.modules.auth.models import User, Role


class UsersDAO(BaseRepository):
    model = User


class RoleDAO(BaseRepository):
    model = Role
