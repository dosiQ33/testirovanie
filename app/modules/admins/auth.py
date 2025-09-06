from fastapi import APIRouter, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database.deps import get_session_without_commit
from app.modules.auth.utils import verify_password, set_employee_tokens
from app.modules.admins.repository import EmployeesRepo
from app.modules.admins.dtos import EmployeeLoginDto, EmployeeInfoDto
from app.modules.admins.models import Employees
from app.modules.admins.deps import get_current_employee_bearer

router = APIRouter(tags=["admin panel:"])


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

    tokens = set_employee_tokens(response, employee.id)

    logger.info(f"Сотрудник {employee.login} успешно авторизовался")

    return {
        "ok": True,
        "message": "Авторизация успешна!",
        "employee_id": employee.id,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }


@router.get("/test-protected")
async def test_protected_endpoint(
    current_employee: Employees = Depends(get_current_employee_bearer),
) -> dict:
    """Тестовый защищенный эндпоинт для проверки Bearer авторизации"""
    return {
        "message": "Доступ разрешен!",
        "employee_id": current_employee.id,
        "employee_login": current_employee.login,
        "employee_role": current_employee.role,
    }
