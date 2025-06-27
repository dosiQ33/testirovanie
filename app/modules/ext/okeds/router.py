from fastapi import APIRouter

from app.modules.common.router import BaseExtRouter
from .dtos import OkedsDto
from .models import Okeds
from .repository import OkedsRepo


router = APIRouter(prefix="/okeds")

okeds = BaseExtRouter(
    "okeds",
    Okeds,
    OkedsRepo,
    OkedsDto,
    tags=["ext: okeds"],
)

router.include_router(okeds)
