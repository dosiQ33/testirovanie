from fastapi import APIRouter, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database.deps import get_session_with_commit, get_session_without_commit
from app.modules.auth.utils import verify_password, set_tokens
from app.modules.admins.repository import EmployeesRepo
from app.modules.admins.dtos import EmployeeLoginDto, EmployeeInfoDto
from app.modules.admins.models import Employees

router = APIRouter(prefix="/admins/auth")


@router.post("/login/")
async def login_employee(
    response: Response,
    login_data: EmployeeLoginDto,
    session: AsyncSession = Depends(get_session_without_commit),
) -> dict:
    """
    Авторизация сотрудника по логину и паролю
    """
    employees_repo = EmployeesRepo(session)
    employee = await employees_repo.get_by_login(login_data.login)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный логин или пароль"
        )

    if employee.deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учетная запись удалена"
        )

    if employee.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учетная запись заблокирована"
        )

    if not verify_password(login_data.password, employee.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный логин или пароль"
        )

    set_tokens(response, employee.id)

    logger.info(f"Сотрудник {employee.login} успешно авторизовался")

    return {"ok": True, "message": "Авторизация успешна!", "employee_id": employee.id}


@router.post("/logout")
async def logout_employee(response: Response):
    """Выход сотрудника из системы"""
    response.delete_cookie("employee_access_token")
    response.delete_cookie("employee_refresh_token")
    return {"message": "Сотрудник успешно вышел из системы"}
