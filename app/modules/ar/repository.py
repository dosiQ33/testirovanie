"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from sqlalchemy import select

from app.modules.common.repository import BaseRepository
from .models import DAtsTypes, DBuildingsPointers, DGeonimsTypes, DRoomsTypes, SAts, SGeonims, SGrounds, SBuildings, SPb


class DAtsTypesRepo(BaseRepository):
    model = DAtsTypes


class DBuildingsPointersRepo(BaseRepository):
    model = DBuildingsPointers


class DGeonimsTypesRepo(BaseRepository):
    model = DGeonimsTypes


class DRoomsTypesRepo(BaseRepository):
    model = DRoomsTypes


class SAtsRepo(BaseRepository):
    model = SAts


class SGeonimsRepo(BaseRepository):
    model = SGeonims


class SGroundsRepo(BaseRepository):
    model = SGrounds


class SBuildingsRepo(BaseRepository):
    model = SBuildings

    async def find_by_pathnames_and_number(self, path_names: list[str], number: str):
        query = select(self.model)
        query = query.filter(SBuildings.path_names_ru.contains(path_names), SBuildings.number == number)

        result = await self._session.execute(query)
        return result.unique().scalars().all()


class SPbRepo(BaseRepository):
    model = SPb
