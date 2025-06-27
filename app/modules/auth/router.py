from typing import List
from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.auth.utils import authenticate_user, set_tokens
from app.modules.auth.deps import (
    get_current_user,
    get_current_admin_user,
    check_refresh_token,
)
from app.database.deps import get_session_with_commit, get_session_without_commit
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from app.modules.auth.repository import UsersDAO
from app.modules.auth.dtos import (
    RegisterUserDto,
    AuthUserDto,
    EmailDto,
    AddUserDto,
    UserInfoDto,
)

router = APIRouter(prefix="/auth")


@router.post("/register/")
async def register_user(user_data: RegisterUserDto, session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    # Проверка существования пользователя
    user_dao = UsersDAO(session)

    existing_user = await user_dao.get_one(filters=EmailDto(email=user_data.email))
    if existing_user:
        raise UserAlreadyExistsException

    # Подготовка данных для добавления
    user_data_dict = user_data.model_dump()
    user_data_dict.pop("confirm_password", None)

    # Добавление пользователя
    await user_dao.add(values=AddUserDto(**user_data_dict))

    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(
    response: Response,
    user_data: AuthUserDto,
    session: AsyncSession = Depends(get_session_without_commit),
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.get_one(filters=EmailDto(email=user_data.email))

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {"ok": True, "message": "Авторизация успешна!"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> UserInfoDto:
    return UserInfoDto.model_validate(user_data)


@router.get("/all_users/")
async def get_all_users(
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_admin_user),
) -> List[UserInfoDto]:
    return await UsersDAO(session).get_many()


@router.post("/refresh")
async def process_refresh_token(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
