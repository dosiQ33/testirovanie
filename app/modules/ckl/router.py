from fastapi import APIRouter

from .transport.router import router as transport_router
from .infra.router import router as infra_router

router = APIRouter(prefix='/ckl')

router.include_router(transport_router)
router.include_router(infra_router)