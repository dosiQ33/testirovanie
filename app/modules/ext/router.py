"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import APIRouter

from .kazgeodesy.router import router as kazgeodesy_router
from .okeds.router import router as okeds_router
from .minerals.router import router as minerals_router

router = APIRouter(prefix="/ext")


router.include_router(kazgeodesy_router)
router.include_router(okeds_router)
router.include_router(minerals_router)
