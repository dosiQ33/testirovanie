from typing import Annotated, List
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit, get_session_without_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl

from .dtos import (
    GtinNpDto,
    GtinKkmsDto,
    GtinNpFilterDto,
    GtinKkmsFilterDto,
    GtinTotalDto,
    GtinTotalFilterDto,
)
from .models import GtinNp, GtinKkms, GtinTotal
from .repository import GtinNpRepo, GtinKkmsRepo, GtinTotalRepo


router = APIRouter(prefix="/product-analytics", tags=["product-analytics"])


class GtinNpRouter(APIRouter):
    """Роутер для GTIN по налогоплательщикам"""

    sub_router = APIRouter(prefix="/gtin-np", tags=["product-analytics: gtin-np"])
    base_router = BaseCRUDRouter(
        "gtin-np",
        GtinNp,
        GtinNpRepo,
        GtinNpDto,
        tags=["product-analytics: gtin-np"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", response_model=List[GtinNpDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_gtin_np(
        filters: Annotated[GtinNpFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """
        Фильтрация GTIN по налогоплательщикам

        - **dtype**: тип данных
        - **org_id**: ID организации
        - **gtin**: GTIN код
        """
        response = await GtinNpRepo(session).filter(filters)
        return [GtinNpDto.model_validate(item) for item in response]

    @sub_router.get("/by-organization/{org_id}", response_model=List[GtinNpDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_organization(
        org_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить все GTIN для организации"""
        response = await GtinNpRepo(session).get_by_organization_id(org_id)
        return [GtinNpDto.model_validate(item) for item in response]


class GtinKkmsRouter(APIRouter):
    """Роутер для GTIN по ККМ"""

    sub_router = APIRouter(prefix="/gtin-kkms", tags=["product-analytics: gtin-kkms"])
    base_router = BaseCRUDRouter(
        "gtin-kkms",
        GtinKkms,
        GtinKkmsRepo,
        GtinKkmsDto,
        tags=["product-analytics: gtin-kkms"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", response_model=List[GtinKkmsDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_gtin_kkms(
        filters: Annotated[GtinKkmsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """
        Фильтрация GTIN по ККМ

        - **dtype**: тип данных
        - **kkms_id**: ID ККМ
        - **gtin**: GTIN код
        """
        response = await GtinKkmsRepo(session).filter(filters)
        return [GtinKkmsDto.model_validate(item) for item in response]

    @sub_router.get("/by-kkm/{kkms_id}", response_model=List[GtinKkmsDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_kkm(
        kkms_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить все GTIN для ККМ"""
        response = await GtinKkmsRepo(session).get_by_kkm_id(kkms_id)
        return [GtinKkmsDto.model_validate(item) for item in response]


class GtinTotalRouter(APIRouter):
    """Роутер для GTIN общей статистики"""

    sub_router = APIRouter(prefix="/gtin-total", tags=["product-analytics: gtin-total"])
    base_router = BaseCRUDRouter(
        "gtin-total",
        GtinTotal,
        GtinTotalRepo,
        GtinTotalDto,
        tags=["product-analytics: gtin-total"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filter", response_model=List[GtinTotalDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def filter_gtin_total(
        filters: Annotated[GtinTotalFilterDto, Query()],
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """
        Фильтрация GTIN общей статистики

        - **dtype**: тип данных
        - **kkms_id**: ID ККМ
        - **gtin**: GTIN код
        """
        response = await GtinTotalRepo(session).filter(filters)
        return [GtinTotalDto.model_validate(item) for item in response]

    @sub_router.get("/by-kkm/{kkms_id}", response_model=List[GtinTotalDto])
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_kkm(
        kkms_id: int,
        session: AsyncSession = Depends(get_session_without_commit),
    ):
        """Получить все GTIN для ККМ"""
        response = await GtinTotalRepo(session).get_by_kkm_id(kkms_id)
        return [GtinTotalDto.model_validate(item) for item in response]


# Подключение роутеров
router.include_router(GtinNpRouter())
router.include_router(GtinKkmsRouter())
router.include_router(GtinTotalRouter())
