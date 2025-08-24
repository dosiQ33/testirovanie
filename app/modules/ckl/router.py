from fastapi import APIRouter

from .transport.router import router as vehicles_router

router = APIRouter(prefix='/ckl')

router.include_router(vehicles_router)