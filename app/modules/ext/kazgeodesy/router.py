from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseExtRouter
from .dtos import KazgeodesyRkDto, KazgeodesyRkWithGeomDto
from .models import KazgeodesyRkOblasti, KazgeodesyRkRaiony
from .repository import KazgeodesyRkOblastiRepo, KazgeodesyRkRaionyRepo


router = APIRouter(prefix="/kazgeodesy")


class OblastiRouter(APIRouter):
    sub_router = APIRouter(prefix="/rk-oblasti", tags=["ext: kazgeodesy-rk-oblasti"])
    base_router = BaseExtRouter(
        "rk-oblasti",
        KazgeodesyRkOblasti,
        KazgeodesyRkOblastiRepo,
        KazgeodesyRkDto,
        tags=["ext: kazgeodesy-rk-oblasti"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/geom/{id}")
    # @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_geom(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> KazgeodesyRkWithGeomDto:
        return await KazgeodesyRkOblastiRepo(session).get_geom(id)


class RaionyRouter(APIRouter):
    sub_router = APIRouter(prefix="/rk-raiony", tags=["ext: kazgeodesy-rk-raiony"])
    base_router = BaseExtRouter(
        "rk-raiony",
        KazgeodesyRkRaiony,
        KazgeodesyRkRaionyRepo,
        KazgeodesyRkDto,
        tags=["ext: kazgeodesy-rk-raiony"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/geom/{id}")
    # @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_geom(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> KazgeodesyRkWithGeomDto:
        return await KazgeodesyRkRaionyRepo(session).get_geom(id)


router.include_router(OblastiRouter())
router.include_router(RaionyRouter())
