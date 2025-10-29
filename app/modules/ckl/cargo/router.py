from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl

from .dtos import (
    CargosDto
)

from .models import (
    Cargos
)

from .repository import (
    CargosRepository
)

router = APIRouter(prefix="/cargo")

class CargosRouter(APIRouter):
    sub_router = APIRouter(prefix="/cargos", tags=["ckl-cargos: cargos"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "cargos",
            Cargos,
            CargosRepository,
            CargosDto,
            tags=["ckl-cargos: cargos"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{document_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_cargo_info_by_last_document(
        document_id: int, session: AsyncSession = Depends(get_session_with_commit)
    ):
        response = await CargosRepository(session).get_cargo_info(document_id)

        return response


router.include_router(CargosRouter())