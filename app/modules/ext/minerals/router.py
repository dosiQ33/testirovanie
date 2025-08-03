from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import BaseExtRouter, request_key_builder, cache_ttl
from app.modules.common.dto import TerritoryFilterDto
from app.modules.ext.minerals.dtos import (
    MineralsLocContractsDto,
    MineralsLocContractsFilterDto,
    IucMineralsDto,
    IucMineralsFilterRequestDto,
    IucMineralsResponseDto,
    IucMineralsContractsResponseListDto,
)
from app.modules.ext.minerals.models import (
    MineralsLocContracts,
    IucMinerals
)
from app.modules.ext.minerals.repository import (
    MineralsLocContractsRepo, 
    IucMineralsRepo
)



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

class IucMineralsRouter(APIRouter):
    sub_router = APIRouter(prefix='/iuc-minerals', tags=['ext: iuc-minerals'])
    base_router = BaseExtRouter(
        'iuc-minerals',
        IucMinerals,
        IucMineralsRepo,
        IucMineralsDto,
        tags=['ext: iuc-minerals']
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/filters")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_filtered_minerals(
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucMineralsRepo(session).get_filters()

        return response
    
    @sub_router.get("/info-by-id/{id}", response_model=IucMineralsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_minerals_info_by_id(
        id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucMineralsRepo(session).get_minerals_info_by_id(id)

        return response
    
    @sub_router.get("/contracts/by-territory", response_model=IucMineralsContractsResponseListDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_contracts_by_territory(
        filter: Annotated[TerritoryFilterDto, Query()],
        session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await IucMineralsRepo(session).get_contracts_by_territory(filter)

        return response


router.include_router(MineralsLocContractsRouter())
router.include_router(IucMineralsRouter())
