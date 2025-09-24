from typing import Annotated, List
from fastapi import APIRouter, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit
from app.modules.common.router import (
    BaseCRUDRouter,
    request_key_builder,
    cache_ttl,
    PaginatedResponse,
)
from .dtos import (
    DicOrderStatusDto,
    DicOrderTypeDto,
    DicRiskDegreeDto,
    DicRiskNameDto,
    ExecFilesCreateDto,
    ExecFilesDto,
    ExecFilesFilterDto,
    ExecutionsCreateDto,
    ExecutionsDto,
    ExecutionsFilterDto,
    OrderPatchDto,
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
    ExecFiles,
    Executions,
    Risks,
    Orders,
)
from .repository import (
    DicOrderStatusRepo,
    DicOrderTypeRepo,
    DicRiskDegreeRepo,
    DicRiskNameRepo,
    DicRiskTypeRepo,
    ExecFilesRepo,
    ExecutionsRepo,
    RisksRepo,
    OrdersRepo,
)
from .filters import ExecFilesFilter, ExecutionsFilter, RisksFilter, OrdersFilter


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
        page_size: int | None = None,
        page: int | None = None,
        risk_degree_id: int | None = None,
        risk_type_id: int | None = None,
        risk_name_id: int | None = None,
        iin_bin: str | None = None,
        is_ordered: bool | None = None,
        region: str | None = None,
        city: str | None = None,
        district: str | None = None,
        village: str | None = None,
        territory: str | None = None,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> PaginatedResponse[RisksDto]:
        """
        Получить риски с детальной информацией (аналог SQL запроса с JOIN) с поддержкой пагинации

        - **page_size**: размер страницы (количество записей на странице)
        - **page**: номер страницы (начиная с 1)
        - **risk_degree_id**: фильтр по степени риска (опционально)
        - **risk_type_id**: фильтр по типу риска (опционально)
        - **risk_name_id**: фильтр по наименованию риска (опционально)
        - **iin_bin**: фильтр по ИИН/БИН организации (опционально)
        - **is_ordered**: фильтр по статусу назначения (True - назначен, False - не назначен, None - все)
        - **region**: фильтр по региону организации (опционально)
        - **city**: фильтр по городу организации (опционально)
        - **district**: фильтр по району организации (опционально)
        - **village**: фильтр по селу/деревне организации (опционально)

        Возвращает пагинированный список рисков с информацией о:
        - общем количестве записей
        - текущей странице
        - общем количестве страниц
        """
        filters = RisksFilterDto(
            risk_degree_id=risk_degree_id,
            risk_type_id=risk_type_id,
            risk_name_id=risk_name_id,
            iin_bin=iin_bin,
            is_ordered=is_ordered,
            region=region,
            city=city,
            district=district,
            village=village,
            territory=territory
        )

        response, total = await RisksRepo(session).get_risks_with_details(
            filters=filters, page_size=page_size, page=page
        )

        current_page = page or 1
        total_pages = (
            (total // page_size + int(total % page_size > 0)) if page_size else 1
        )

        return PaginatedResponse[RisksDto](
            data=[RisksDto.model_validate(item) for item in response],
            page=current_page,
            total=total,
            page_count=total_pages,
        )

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

        existing_risk = await repo.get_risk_by_id(risk_id)
        if not existing_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Риск с ID {risk_id} не найден",
            )

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
        reloaded_order = await repo.get_one_by_id(new_order.id)

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

    @sub_router.patch("/{order_id}")
    async def patch_order(
        order_id: int,
        order_data: OrderPatchDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> OrdersDto:
        """
        Частично обновить поручение (обновляются только переданные поля)

        - **order_id**: ID поручения для обновления
        - **order_deadline**: срок исполнения (опционально)
        - **order_num**: номер поручения (опционально)
        - **employee_id**: ID сотрудника (опционально)
        - **order_status**: статус поручения (опционально)
        - **order_type**: тип поручения (опционально)
        - **order_desc**: описание поручения (опционально)
        - **step_count**: количество шагов (опционально)
        - **sign**: подпись (опционально)

        Все поля опциональны. Будут обновлены только те поля, которые переданы в запросе.
        """
        repo = OrdersRepo(session)

        updated_order = await repo.patch_order(order_id, order_data)

        reloaded_order = await repo.get_one_by_id(updated_order.id)

        return OrdersDto.model_validate(reloaded_order)


class ExecutionsRouter(APIRouter):
    sub_router = APIRouter(prefix="/executions", tags=["orders: executions"])
    base_router = BaseCRUDRouter(
        "executions",
        Executions,
        ExecutionsRepo,
        ExecutionsDto,
        ExecutionsFilter,
        tags=["orders: executions"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.post("/")
    async def create_execution(
        execution_data: ExecutionsCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> ExecutionsDto:
        """
        Create new execution

        - **exec_date**: execution date
        - **exec_text**: execution text
        - **order_id**: order ID
        - **exec_num**: execution number
        - **employee_id**: employee ID
        - **is_accepted**: accepted status
        - **sign**: signature
        """
        repo = ExecutionsRepo(session)
        new_execution = await repo.add(execution_data)
        reloaded_execution = await repo.get_one_by_id(new_execution.id)
        return ExecutionsDto.model_validate(reloaded_execution)

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_executions(
        filters: Annotated[ExecutionsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ExecutionsDto]:
        """
        Get executions with filtering

        - **exec_date_from**: execution date from
        - **exec_date_to**: execution date to
        - **order_id**: order ID
        - **exec_num**: execution number
        - **employee_id**: employee ID
        - **is_accepted**: accepted status
        """
        response = await ExecutionsRepo(session).filter_executions(filters)
        return [ExecutionsDto.model_validate(item) for item in response]

    @sub_router.get("/by-order/{order_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_executions_by_order(
        order_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ExecutionsDto]:
        """Get all executions for a specific order"""
        response = await ExecutionsRepo(session).get_by_order_id(order_id)
        return [ExecutionsDto.model_validate(item) for item in response]


class ExecFilesRouter(APIRouter):
    sub_router = APIRouter(prefix="/exec-files", tags=["orders: exec-files"])
    base_router = BaseCRUDRouter(
        "exec-files",
        ExecFiles,
        ExecFilesRepo,
        ExecFilesDto,
        ExecFilesFilter,
        tags=["orders: exec-files"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.post("/")
    async def create_exec_file(
        file_data: ExecFilesCreateDto,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> ExecFilesDto:
        """
        Create new execution file

        - **name**: file display name
        - **file_name**: actual file name
        - **exec_id**: execution ID
        - **ext**: file extension
        - **type**: file type
        - **length**: file size
        - **path**: file path
        """
        repo = ExecFilesRepo(session)
        new_file = await repo.add(file_data)
        reloaded_file = await repo.get_one_by_id(new_file.id)
        return ExecFilesDto.model_validate(reloaded_file)

    @sub_router.get("/filter")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_exec_files(
        filters: Annotated[ExecFilesFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ExecFilesDto]:
        """
        Get execution files with filtering

        - **exec_id**: execution ID
        - **name**: file display name
        - **file_name**: actual file name
        - **ext**: file extension
        - **type**: file type
        - **created_from**: created date from
        - **created_to**: created date to
        """
        response = await ExecFilesRepo(session).filter_exec_files(filters)
        return [ExecFilesDto.model_validate(item) for item in response]

    @sub_router.get("/by-execution/{exec_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_files_by_execution(
        exec_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ExecFilesDto]:
        """Get all files for a specific execution"""
        response = await ExecFilesRepo(session).get_by_exec_id(exec_id)
        return [ExecFilesDto.model_validate(item) for item in response]


# Подключение всех роутеров
router.include_router(dic_order_status_router)
router.include_router(dic_order_type_router)
router.include_router(dic_risk_degree_router)
router.include_router(dic_risk_name_router)
router.include_router(dic_risk_type_router)
router.include_router(RisksRouter())
router.include_router(OrdersRouter())
router.include_router(ExecutionsRouter())
router.include_router(ExecFilesRouter())
