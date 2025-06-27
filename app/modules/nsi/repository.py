"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from app.modules.common.repository import BaseRepository
from .models import RiskDegrees, Ugds, OkedsOld, TaxRegimes, RegTypes


class UgdsRepo(BaseRepository):
    model = Ugds


class OkedsRepo(BaseRepository):
    model = OkedsOld


class TaxRegimesRepo(BaseRepository):
    model = TaxRegimes


class RegTypesRepo(BaseRepository):
    model = RegTypes


class RiskDegreesRepo(BaseRepository):
    model = RiskDegrees
