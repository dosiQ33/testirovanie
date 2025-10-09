from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import request_key_builder, cache_ttl
from app.modules.common.router import BaseCRUDRouter

from .models import (
    Roads,
    RoadServices
)

from .dtos import (
    RoadsDto,
    RoadServicesDto
)

from .repository import (
    RoadsRepo,
    RoadServicesRepo
)

router = APIRouter(prefix="/infra")

class RoadsRouter(APIRouter):
    sub_router = APIRouter(prefix="/roads", tags=["ckl: roads"])
    base_router = BaseCRUDRouter(
        "roads", Roads, RoadsRepo, RoadsDto, tags=["ckl: roads"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{road_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_road_info(
        road_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await RoadsRepo(session).get_road_info(road_id)

        return response
    
    @sub_router.get("/count/{road_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_road_data(
        road_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await RoadsRepo(session).get_road_data(road_id)

        return response
    
class RoadsServicesRouter(APIRouter):
    sub_router = APIRouter(prefix="/road-services", tags=["ckl: road-services"])
    base_router = BaseCRUDRouter(
        "road-seervices", RoadServices, RoadServicesRepo, RoadServicesDto, tags=["ckl: road-services"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{service_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_road_services_reg_info(
        service_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await RoadServicesRepo(session).get_road_services_reg_info(service_id)

        return response
    
    @sub_router.get("/geo/{service_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_road_services_geo_info(
        service_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await RoadServicesRepo(session).get_road_services_geo_info(service_id)

        return response
    
    @sub_router.get("/infra/{service_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_road_services_infrastructure(
        service_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await RoadServicesRepo(session).get_road_services_infrastructure(service_id)

        return response

router.include_router(RoadsRouter())
router.include_router(RoadsServicesRouter())