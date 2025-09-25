from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import request_key_builder, cache_ttl
from app.modules.common.router import BaseCRUDRouter

from app.modules.common.router import ORJsonCoder

from .models import (
    Vehicles,
    TransportCompanies,
    Warehouses
)

from .dtos import (
    VehiclesDto,
    TransportCompaniesDto,
    VehicleGeoInfoResponse,
    WarehousesDto
)

from .repository import (
    VehiclesRepo,
    TransportCompaniesRepo,
    WarehousesRepository
)

router = APIRouter(prefix="/transport")


class VehiclesRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicles", tags=["ckl: vehicles"])
    base_router = BaseCRUDRouter(
        "vehicles", Vehicles, VehiclesRepo, VehiclesDto, tags=["ckl: vehicles"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{vehicle_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_vehicle_info(
        vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await VehiclesRepo(session).get_vehicle_info(vehicle_id)

        return response
    
    @sub_router.get("/geo-info/{vehicle_id}", response_model=VehicleGeoInfoResponse)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_vehicle_position_info(
        vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await VehiclesRepo(session).get_vehicle_position_info(vehicle_id)

        return response
    

    @sub_router.get("/entrypoints/{vehicle_id}",)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_vehicle_entrypoints(
        vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await VehiclesRepo(session).get_entrypoints(vehicle_id)

        return response
    
    @sub_router.get("/interpoints/{vehicle_id}",)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_vehicle_entrypoints(
        vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await VehiclesRepo(session).get_intermediate_points(vehicle_id)

        return response
    
class TransportCompaniesRouter(APIRouter):
    sub_router = APIRouter(prefix="/transport-companies", tags=["ckl: transport companies"])
    base_router = BaseCRUDRouter(
        "transport-companies", TransportCompanies, TransportCompaniesRepo, TransportCompaniesDto, tags=["ckl: transport companies"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{company_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_transport_company_info(
        company_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await TransportCompaniesRepo(session).get_base_info(company_id)

        return response
    
    @sub_router.get("/count/{company_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_transport_count(
        company_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await TransportCompaniesRepo(session).get_transport_info(company_id)

        return response
    
    @sub_router.get("/info")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_all_transport_companies(
        session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await TransportCompaniesRepo(session).get_all_transport_comapnies()

        return response
    
class WarehousesRouter(APIRouter):
    sub_router = APIRouter(prefix="/warehouses", tags=["ckl: warehouses"])
    base_router = BaseCRUDRouter(
        "warehouses", Warehouses, WarehousesRepository, WarehousesDto, tags=["ckl: warehouses"]
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{warehouse_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_warehouse_info(
        warehouse_id: int,
        session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await WarehousesRepository(session).get_warehouse_info(warehouse_id)

        return response

router.include_router(VehiclesRouter())
router.include_router(TransportCompaniesRouter())
router.include_router(WarehousesRouter())