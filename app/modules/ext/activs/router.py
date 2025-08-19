from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit

from app.modules.common.router import BaseExtRouter, request_key_builder, cache_ttl
from app.modules.common.dto import TerritoryFilterDto

from .dtos import (
    IucAlkoDto,
    IucNeftebasaCoordinatesTempDto,
    IucNpzCoordinatesTempDto,
    IucAzsCoordinatesTempDto,
    IucZernoCoordinatesTempDto,
    IucAlkoResponseDto,
    IucAzsResponseDto,
    IucNeftebasaResponseDto,
    IucZernoResponseDto,
    IucNpzResponseDto
)

from .models import (
    IucAlko,
    IucNeftebasaCoordinatesTemp,
    IucAzsCoordinatesTemp,
    IucNpzCoordinatesTemp,
    IucZernoCoordinatesTemp
)
from .repository import (
    IucAlkoRepository,
    IucNeftebasaRepository,
    IucNpzRepository,
    IucAzsRepository,
    IucZernoRepository
)

router = APIRouter(prefix="/activs")

class IucAlkoRouter(APIRouter):
    sub_router = APIRouter(prefix="/iuc-alko", tags=["ext: iuc-alko"])
    base_router = BaseExtRouter(
        "iuc-alko",
        IucAlko,
        IucAlkoRepository,
        IucAlkoDto,
        tags=["ext: iuc-alko"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{activ_id}", response_model=IucAlkoResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(
        activ_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucAlkoRepository(session).get_info(activ_id)

        return response
    

class IucNeftebasaRouter(APIRouter):
    sub_router = APIRouter(prefix="/iuc-neftebasa", tags=["ext: iuc-neftebasa"])
    base_router = BaseExtRouter(
        "iuc-neftebasa",
        IucNeftebasaCoordinatesTemp,
        IucNeftebasaRepository,
        IucNeftebasaCoordinatesTempDto,
        tags=["ext: iuc-neftebasa"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{activ_id}", response_model=IucNeftebasaResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(
        activ_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucNeftebasaRepository(session).get_info(activ_id)

        return response
    
class IucNpzRouter(APIRouter):
    sub_router = APIRouter(prefix="/iuc-npz", tags=["ext: iuc-npz"])
    base_router = BaseExtRouter(
        "iuc-npz",
        IucNpzCoordinatesTemp,
        IucNpzRepository,
        IucNpzCoordinatesTempDto,
        tags=["ext: iuc-npz"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{activ_id}", response_model=IucNpzResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(
        activ_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucNpzRepository(session).get_info(activ_id)

        return response

class IucAzsRouter(APIRouter):
    sub_router = APIRouter(prefix="/iuc-azs", tags=["ext: iuc-azs"])
    base_router = BaseExtRouter(
        "iuc-azs",
        IucAzsCoordinatesTemp,
        IucAzsRepository,
        IucAzsCoordinatesTempDto,
        tags=["ext: iuc-azs"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{activ_id}", response_model=IucAzsResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(
        activ_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucAzsRepository(session).get_info(activ_id)

        return response
    
class IucZernoRouter(APIRouter):
    sub_router = APIRouter(prefix="/iuc-zerno", tags=["ext: iuc-zerno"])
    base_router = BaseExtRouter(
        "iuc-zerno",
        IucZernoCoordinatesTemp,
        IucZernoRepository,
        IucZernoCoordinatesTempDto,
        tags=["ext: iuc-zerno"],
    )

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{activ_id}", response_model=IucZernoResponseDto)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(
        activ_id: int,
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        response = await IucZernoRepository(session).get_info(activ_id)

        return response


router.include_router(IucAlkoRouter())
router.include_router(IucNeftebasaRouter())
router.include_router(IucNpzRouter())
router.include_router(IucAzsRouter())
router.include_router(IucZernoRouter())