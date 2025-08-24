from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import BaseExtRouter, request_key_builder, cache_ttl
from app.modules.common.router import BaseCRUDRouter

from .models import (
    Vehicles
)

from .dtos import (
    VehiclesDto
)

from .repository import (
    VehiclesRepo
)

router = APIRouter(prefix="/vehicles")

class VehiclesRouter(APIRouter):
    sub_router = APIRouter(prefix='/vehicles', tags=['ckl: vehicles'])
    base_router = BaseCRUDRouter(
        'vehicles',
        Vehicles,
        VehiclesRepo,
        VehiclesDto,
        tags=['ckl: vehicles']
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self. include_router(self.base_router)

    @sub_router.get("/info/{vehicle_id}", summary="Фильтр по полям")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_vehicle_info(
        vehicle_id: int,
        session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await VehiclesRepo(session).get_vehicle_info(vehicle_id)

        return response

router.include_router(VehiclesRouter())