from fastapi import APIRouter

from .transport.router import router as transport_router
from .infra.router import router as infra_router
from .customs.router import router as customs_router
from .cargo.router import router as cargo_router

router = APIRouter(prefix='/ckl')

router.include_router(transport_router)
router.include_router(infra_router)
router.include_router(customs_router)
router.include_router(cargo_router)