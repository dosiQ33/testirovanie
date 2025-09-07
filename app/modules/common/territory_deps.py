"""
Territory dependency для получения территориальных ограничений пользователя
ИСПРАВЛЕНО: правильная обработка геометрии из PostGIS
Путь: app/modules/common/territory_deps.py
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_AsText
from loguru import logger

from app.modules.admins.models import Employees, DicUl
from app.modules.admins.deps import get_current_employee
from app.modules.ext.kazgeodesy.models import KazgeodesyRkOblasti, KazgeodesyRkRaiony
from app.database.deps import get_session_without_commit


class UserTerritoryInfo:
    """Класс для хранения территориальной информации пользователя"""

    def __init__(
        self,
        territory_level: str,
        territory_id: int,
        territory_name: str,
        territory_geom: Optional[WKTElement] = None,
    ):
        self.territory_level = territory_level  # 'republic', 'oblast', 'raion'
        self.territory_id = territory_id
        self.territory_name = territory_name
        self.territory_geom = territory_geom

    def is_republic_level(self) -> bool:
        return self.territory_level == "republic"

    def should_filter_territory(self) -> bool:
        return not self.is_republic_level()


async def get_user_territory_info(
    current_employee: Employees = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session_without_commit),
) -> UserTerritoryInfo:
    """
    Получить территориальную информацию текущего пользователя
    """
    try:
        # Проверяем является ли пользователь администратором республиканского уровня
        if current_employee.role == 3:  # Администратор
            logger.info(
                f"Пользователь {current_employee.login} имеет республиканский доступ"
            )
            return UserTerritoryInfo(
                territory_level="republic",
                territory_id=0,
                territory_name="Республика Казахстан",
            )

        # Получаем информацию о юридическом лице сотрудника
        if not current_employee.ul_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Сотрудник не привязан к территориальному подразделению",
            )

        # Получаем информацию об организации сотрудника
        query = select(DicUl).where(DicUl.id == current_employee.ul_id)
        result = await session.execute(query)
        dic_ul = result.scalar_one_or_none()

        if not dic_ul:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Территориальное подразделение не найдено",
            )

        territory_info = None

        # Определяем уровень доступа: область или район
        if dic_ul.oblast_id and not dic_ul.raion_id:
            # Областной уровень - получаем геометрию области в WKT формате
            query = select(
                KazgeodesyRkOblasti.id,
                KazgeodesyRkOblasti.name_ru,
                ST_AsText(KazgeodesyRkOblasti.geom).label("geom_wkt"),
            ).where(KazgeodesyRkOblasti.id == dic_ul.oblast_id)

            result = await session.execute(query)
            oblast_row = result.first()

            if oblast_row:
                territory_info = UserTerritoryInfo(
                    territory_level="oblast",
                    territory_id=oblast_row.id,
                    territory_name=oblast_row.name_ru or "Область",
                    territory_geom=(
                        WKTElement(oblast_row.geom_wkt, srid=4326)
                        if oblast_row.geom_wkt
                        else None
                    ),
                )
                logger.info(
                    f"Найдена область: {oblast_row.name_ru} (ID: {oblast_row.id})"
                )

        elif dic_ul.raion_id:
            # Районный уровень - получаем геометрию района в WKT формате
            query = select(
                KazgeodesyRkRaiony.id,
                KazgeodesyRkRaiony.name_ru,
                ST_AsText(KazgeodesyRkRaiony.geom).label("geom_wkt"),
            ).where(KazgeodesyRkRaiony.id == dic_ul.raion_id)

            result = await session.execute(query)
            raion_row = result.first()

            if raion_row:
                territory_info = UserTerritoryInfo(
                    territory_level="raion",
                    territory_id=raion_row.id,
                    territory_name=raion_row.name_ru or "Район",
                    territory_geom=(
                        WKTElement(raion_row.geom_wkt, srid=4326)
                        if raion_row.geom_wkt
                        else None
                    ),
                )
                logger.info(f"Найден район: {raion_row.name_ru} (ID: {raion_row.id})")

        if not territory_info:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Не удалось определить территориальную принадлежность сотрудника",
            )

        logger.info(
            f"Пользователь {current_employee.login} имеет доступ к {territory_info.territory_level}: {territory_info.territory_name}"
        )

        return territory_info

    except HTTPException:
        # Перепрокидываем HTTP исключения как есть
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении территориальной информации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при определении территориальных прав доступа",
        )


async def get_user_territory_geom(
    territory_info: UserTerritoryInfo = Depends(get_user_territory_info),
) -> Optional[WKTElement]:
    """
    Получить геометрию территории пользователя для фильтрации
    Возвращает None если пользователь имеет республиканский доступ
    """
    if territory_info.should_filter_territory():
        return territory_info.territory_geom
    return None
