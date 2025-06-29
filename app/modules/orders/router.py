from typing import Annotated, List
from fastapi import APIRouter, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl
from .dtos import (
    DicOrderStatusDto,
    DicOrderTypeDto,
    DicRiskDegreeDto,
    DicRiskNameDto,
    DicRiskTypeDto,
    RisksDto,
    RisksFilterDto,
    RiskUpdateDto,
    RiskBulkUpdateDto,
    RiskUpdateResponseDto,
    OrderCreateDto,
    OrdersDto,
    OrdersFilterDto,
)
from .models import (
    DicOrderStatus,
    DicOrderType,
    DicRiskDegree,
    DicRiskName,
    DicRiskType,
    Risks,
    Orders,
)
from .repository import (
    DicOrderStatusRepo,
    DicOrderTypeRepo,
    DicRiskDegreeRepo,
    DicRiskNameRepo,
    DicRiskTypeRepo,
    RisksRepo,
    OrdersRepo,
)
from .filters import RisksFilter, OrdersFilter


router = APIRouter(prefix="/orders")

# Базовые CRUD роутеры для справочников
dic_order_status_router = BaseCRUDRouter(
    "dic-order-status",
    DicOrderStatus,
    DicOrderStatusRepo,
    DicOrderStatusDto,
    tags=["orders: dic-order-status"],
)
dic_order_type_router = BaseCRUDRouter(
    "dic-order-type",
    DicOrderType,
    DicOrderTypeRepo,
    DicOrderTypeDto,
    tags=["orders: dic-order-type"],
)
dic_risk_degree_router = BaseCRUDRouter(
    "dic-risk-degree",
    DicRiskDegree,
    DicRiskDegreeRepo,
    DicRiskDegreeDto,
    tags=["orders: dic-risk-degree"],
)
dic_risk_name_router = BaseCRUDRouter(
    "dic-risk-name",
    DicRiskName,
    DicRiskNameRepo,
    DicRiskNameDto,
    tags=["orders: dic-risk-name"],
)
dic_risk_type_router = BaseCRUDRouter(
    "dic-risk-type",
    DicRiskType,
    DicRiskTypeRepo,
    DicRiskTypeDto,
    tags=["orders: dic-risk-type"],
)


class RisksRouter(APIRouter):
    sub_router = APIRouter(prefix="/risks", tags=["orders: risks"])
    base_router = BaseCRUDRouter(
        "risks", Risks, RisksRepo, RisksDto, RisksFilter, tags=["orders: risks"]
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/with-details")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_risks_with_details(
        filters: Annotated[RisksFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[RisksDto]:
        """Получить риски с детальной информацией (аналог SQL запроса с JOIN)"""
        response = await RisksRepo(session).get_risks_with_details(filters)
        return [RisksDto.model_validate(item) for item in response]

    @sub_router.put("/bulk")
    async def bulk_update_risks_order(
        bulk_update: RiskBulkUpdateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> RiskUpdateResponseDto:
        """
        Массовое обновление order_id и/или is_ordered для множества рисков

        - **risk_ids**: список ID рисков для обновления
        - **order_id**: новый ID заказа для всех указанных рисков (опционально)
        - **is_ordered**: новый статус заказа для всех указанных рисков (опционально)
        """
        if not bulk_update.risk_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Список risk_ids не может быть пустым",
            )

        if bulk_update.order_id is None and bulk_update.is_ordered is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Необходимо указать хотя бы одно поле для обновления (order_id или is_ordered)",
            )

        repo = RisksRepo(session)
        updated_count = await repo.bulk_update_risks_order(bulk_update)

        return RiskUpdateResponseDto(
            updated_count=updated_count,
            message=f"Успешно обновлено {updated_count} записей из {len(bulk_update.risk_ids)} запрошенных",
        )

    @sub_router.put("/{risk_id}")
    async def update_risk_order(
        risk_id: int,
        update_data: RiskUpdateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> RiskUpdateResponseDto:
        """
        Обновить order_id и/или is_ordered для одного риска

        - **risk_id**: ID риска для обновления
        - **order_id**: новый ID заказа (опционально)
        - **is_ordered**: новый статус заказа (опционально)
        """
        repo = RisksRepo(session)

        # Проверяем существование записи
        existing_risk = await repo.get_risk_by_id(risk_id)
        if not existing_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Риск с ID {risk_id} не найден",
            )

        # Обновляем запись
        updated_count = await repo.update_risk_order(risk_id, update_data)

        if updated_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось обновить запись или нет данных для обновления",
            )

        return RiskUpdateResponseDto(
            updated_count=updated_count, message=f"Риск с ID {risk_id} успешно обновлен"
        )


class OrdersRouter(APIRouter):
    sub_router = APIRouter(prefix="/orders-list", tags=["orders: orders"])
    base_router = BaseCRUDRouter(
        "orders-list",
        Orders,
        OrdersRepo,
        OrdersDto,
        OrdersFilter,
        tags=["orders: orders"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.post("/")
    async def create_order(
        order_data: OrderCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> OrdersDto:
        """
        Создать новое поручение

        - **order_date**: дата поручения (обязательно)
        - **order_deadline**: срок исполнения (опционально)
        - **order_num**: номер поручения (опционально)
        - **employee_id**: ID сотрудника (опционально)
        - **order_status**: статус поручения (опционально)
        - **order_type**: тип поручения (опционально)
        - **order_desc**: описание поручения (опционально)
        - **step_count**: количество шагов (опционально)
        - **sign**: подпись (опционально)
        """
        repo = OrdersRepo(session)

        new_order = await repo.add(order_data)

        return OrdersDto.model_validate(new_order)

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_orders(
        filters: Annotated[OrdersFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[OrdersDto]:
        """
        Получить список поручений с фильтрацией

        - **order_date_from**: дата поручения от
        - **order_date_to**: дата поручения до
        - **order_deadline_from**: срок исполнения от
        - **order_deadline_to**: срок исполнения до
        - **order_num**: номер поручения
        - **employee_id**: ID сотрудника
        - **order_status**: статус поручения
        - **order_type**: тип поручения
        """
        response = await OrdersRepo(session).filter_orders(filters)
        return [OrdersDto.model_validate(item) for item in response]

    @sub_router.get("/{id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_order_by_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> OrdersDto:
        """Получить поручение по ID"""
        repo = OrdersRepo(session)
        order = await repo.get_one_by_id(id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Поручение с ID {id} не найдено",
            )

        return OrdersDto.model_validate(order)


# Подключение всех роутеров
router.include_router(dic_order_status_router)
router.include_router(dic_order_type_router)
router.include_router(dic_risk_degree_router)
router.include_router(dic_risk_name_router)
router.include_router(dic_risk_type_router)
router.include_router(RisksRouter())
router.include_router(OrdersRouter())
