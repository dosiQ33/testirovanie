from typing import Annotated, List
from fastapi import APIRouter, Query
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
)
from .models import (
    DicOrderStatus,
    DicOrderType,
    DicRiskDegree,
    DicRiskName,
    DicRiskType,
    Risks,
)
from .repository import (
    DicOrderStatusRepo,
    DicOrderTypeRepo,
    DicRiskDegreeRepo,
    DicRiskNameRepo,
    DicRiskTypeRepo,
    RisksRepo,
)
from .filters import RisksFilter


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
        """
        Получить риски с детальной информацией (аналог SQL запроса с JOIN)
        """
        response = await RisksRepo(session).get_risks_with_details(filters)
        return [RisksDto.model_validate(item) for item in response]


# Подключение всех роутеров
router.include_router(dic_order_status_router)
router.include_router(dic_order_type_router)
router.include_router(dic_risk_degree_router)
router.include_router(dic_risk_name_router)
router.include_router(dic_risk_type_router)
router.include_router(RisksRouter())
