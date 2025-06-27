"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter
from .dtos import (
    AddBuildingCoordsDto,
    DAtsTypesDto,
    DBuildingsPointersDto,
    DGeonimsTypesDto,
    DRoomsTypesDto,
    SAtsDto,
    SBuildingsDto,
    SGeonimsDto,
    SGroundsDto,
    SPbDto,
)
from .models import DAtsTypes, DBuildingsPointers, DGeonimsTypes, DRoomsTypes, SAts, SBuildings, SGeonims, SGrounds, SPb
from .repository import (
    DAtsTypesRepo,
    DBuildingsPointersRepo,
    DGeonimsTypesRepo,
    DRoomsTypesRepo,
    SAtsRepo,
    SBuildingsRepo,
    SGeonimsRepo,
    SGroundsRepo,
    SPbRepo,
)


router = APIRouter(prefix="/ar")

d_ats_types_router = BaseCRUDRouter("d-ats-types", DAtsTypes, DAtsTypesRepo, DAtsTypesDto, tags=["ar: d-ats-types"])
d_buildings_pointers_router = BaseCRUDRouter(
    "d-buildings-pointers", DBuildingsPointers, DBuildingsPointersRepo, DBuildingsPointersDto, tags=["ar: d-buildings-pointers"]
)
d_geonims_types_router = BaseCRUDRouter(
    "d-geonims-types", DGeonimsTypes, DGeonimsTypesRepo, DGeonimsTypesDto, tags=["ar: d-geonims-types"]
)
d_rooms_types_router = BaseCRUDRouter("d-rooms-types", DRoomsTypes, DRoomsTypesRepo, DRoomsTypesDto, tags=["ar: d-rooms-types"])


class SAtsRouter(APIRouter):
    sub_router = APIRouter(prefix="/s-ats", tags=["ar: s-ats"])
    base_router = BaseCRUDRouter("s-ats", SAts, SAtsRepo, SAtsDto, tags=["ar: s-ats"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""


class SGeonimsRouter(APIRouter):
    sub_router = APIRouter(prefix="/s-geonims", tags=["ar: s-geonims"])
    base_router = BaseCRUDRouter("s-geonims", SGeonims, SGeonimsRepo, SGeonimsDto, tags=["ar: s-geonims"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""


class SGroundsRouter(APIRouter):
    sub_router = APIRouter(prefix="/s-grounds", tags=["ar: s-grounds"])
    base_router = BaseCRUDRouter("s-grounds", SGrounds, SGroundsRepo, SGroundsDto, tags=["ar: s-grounds"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""


class SBuildingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/s-buildings", tags=["ar: s-buildings"])
    base_router = BaseCRUDRouter("s-buildings", SBuildings, SBuildingsRepo, SBuildingsDto, tags=["ar: s-buildings"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""

    @sub_router.post("/add-coords")
    async def add_coords(dto: AddBuildingCoordsDto, session: AsyncSession = Depends(get_session_with_commit)):
        if dto.building_number is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не указан номер дома")

        _path_names = [dto.street, dto.locality_district, dto.locality, dto.district, dto.region]
        path_names = [x for x in _path_names if x is not None]

        if not path_names:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Слишком короткий адрес")

        if len(path_names) < 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Слишком короткий адрес")

        buildings = await SBuildingsRepo(session).find_by_pathnames_and_number(
            path_names=path_names,
            number=dto.building_number,
        )

        if not buildings:
            # TODO: add logic for creating new building
            return True

        for building in buildings:
            # TODO: update building coords
            return True

        return True


class SPbRouter(APIRouter):
    sub_router = APIRouter(prefix="/s-pb", tags=["ar: s-pb"])
    base_router = BaseCRUDRouter("s-pb", SPb, SPbRepo, SPbDto, tags=["ar: s-pb"])

    def __init__(self):
        super().__init__()

        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    """Own routes"""


router.include_router(d_ats_types_router)
router.include_router(d_buildings_pointers_router)
router.include_router(d_geonims_types_router)
router.include_router(d_rooms_types_router)
router.include_router(SAtsRouter())
router.include_router(SGeonimsRouter())
router.include_router(SGroundsRouter())
router.include_router(SBuildingsRouter())
router.include_router(SPbRouter())
