from fastapi import APIRouter, HTTPException, Query, status
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from loguru import logger
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit, get_session_without_commit

from app.modules.common.router import (
    BaseCRUDRouter,
    request_key_builder,
    cache_ttl,
)

from .dtos import (
    LandsDto,
    LandsLegalInfoDto,
    InfrastructureInfoDto,
    EcologyInfoDto
)

from .models import (
    Lands
)

from .repository import (
   LandsRepository
)

router = APIRouter(prefix="/egkn")

class LandsRouter(APIRouter):
    sub_router = APIRouter(prefix="/lands", tags=["egkn: lands"])
    base_router = BaseCRUDRouter(
        "lands",
        Lands,
        LandsRepository,
        LandsDto,
        tags=["egkn: lands"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get('/legal-info/{land_id}', response_model=LandsLegalInfoDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_legal_information(
        land_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await LandsRepository(session).get_legal_information(land_id)

        return response


    @sub_router.get('/infrastructure/{land_id}', response_model=InfrastructureInfoDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_land_infrastructure(
        land_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        
        response = await LandsRepository(session).get_land_infrastructure(land_id)

        return response
    
    @sub_router.get('/ecology/{land_id}', response_model=EcologyInfoDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_ecological_info(
        land_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await LandsRepository(session).get_ecological_info(land_id)

        return response
    
    @sub_router.get('/restrictions/{land_id}')
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_ecological_info(
        land_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await LandsRepository(session).get_land_restrictions(land_id)

        return response    

router.include_router(LandsRouter())