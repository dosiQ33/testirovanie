from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import BaseExtRouter, request_key_builder, cache_ttl
from app.modules.ext.minerals.dtos import MineralsLocContractsDto, MineralsLocContractsFilterDto
from app.modules.ext.minerals.models import MineralsLocContracts
from app.modules.ext.minerals.repository import MineralsLocContractsRepo


router = APIRouter(prefix="/minerals")


class MineralsLocContractsRouter(APIRouter):
    sub_router = APIRouter(prefix="/loc-contracts", tags=["ext: minerals-loc-contracts"])
    base_router = BaseExtRouter(
        "loc-contracts",
        MineralsLocContracts,
        MineralsLocContractsRepo,
        MineralsLocContractsDto,
        tags=["ext: minerals-loc-contracts"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.get("/filter", summary="Фильтр по полям")
    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def filter(
        filters: Annotated[MineralsLocContractsFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[MineralsLocContractsDto]:
        response = await MineralsLocContractsRepo(session).filter(filters)
        return [MineralsLocContractsDto.model_validate(item) for item in response]


router.include_router(MineralsLocContractsRouter())
