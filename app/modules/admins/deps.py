from datetime import datetime, timezone
from fastapi import Request, Depends, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admins.repository import EmployeesRepo
from app.modules.admins.models import Employees
from app.config import settings
from app.database.deps import get_session_without_commit


def get_employee_access_token(request: Request) -> str:
    """Извлекаем access_token сотрудника из кук."""
    token = request.cookies.get("employee_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации отсутствует",
        )
    return token


async def get_current_employee(
    token: str = Depends(get_employee_access_token),
    session: AsyncSession = Depends(get_session_without_commit),
) -> Employees:
    """Проверяем access_token и возвращаем сотрудника."""
    try:
        # Декодируем токен
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
        )

    expire: str = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек"
        )

    employee_id: str = payload.get("sub")
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен"
        )

    employee = await EmployeesRepo(session).get_one_by_id(int(employee_id))
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден"
        )

    if employee.deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учетная запись удалена"
        )

    if employee.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учетная запись заблокирована"
        )

    return employee


async def get_current_admin_employee(
    current_employee: Employees = Depends(get_current_employee),
) -> Employees:
    """Проверяем права сотрудника как администратора."""
    # Предполагаем, что роли 3 и 4 - административные
    if current_employee.role in [3, 4]:
        return current_employee

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа"
    )
