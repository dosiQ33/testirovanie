from fastapi import APIRouter

from .transport.router import router as vehicles_router
from .infra.router import router as infra_router

router = APIRouter(prefix='/ckl')

router.include_router(vehicles_router)
router.include_router(infra_router)