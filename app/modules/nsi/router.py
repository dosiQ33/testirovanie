"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import APIRouter

from app.modules.common.router import BaseCRUDRouter
from .dtos import CommonRefDto, SimpleRefDto
from .models import RiskDegrees, Ugds, TaxRegimes, RegTypes
from .repository import RiskDegreesRepo, UgdsRepo, TaxRegimesRepo, RegTypesRepo


router = APIRouter(prefix="/nsi")

ugds_router = BaseCRUDRouter("ugds", Ugds, UgdsRepo, CommonRefDto, tags=["nsi: ugds"])
tax_regimes_router = BaseCRUDRouter("tax-regimes", TaxRegimes, TaxRegimesRepo, SimpleRefDto, tags=["nsi: tax-regimes"])
reg_types_router = BaseCRUDRouter("reg-types", RegTypes, RegTypesRepo, SimpleRefDto, tags=["nsi: reg-types"])
risk_degrees_router = BaseCRUDRouter("risk-degrees", RiskDegrees, RiskDegreesRepo, SimpleRefDto, tags=["nsi: risk-degrees"])

router.include_router(ugds_router)
router.include_router(tax_regimes_router)
router.include_router(reg_types_router)
router.include_router(risk_degrees_router)
