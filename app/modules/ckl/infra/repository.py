from sqlalchemy import select, func

from app.modules.common.repository import BaseRepository

from ..customs.models import CustomsOffices

from .models import (
    Roads,
    RoadTypes,
    Cameras
)

from ..transport.models import Vehicles

class RoadsRepo(BaseRepository):
    model = Roads

    async def get_road_info(self, road_id: int):
        query = (
            select(
                Roads.name,
                RoadTypes.name_ru
            )
            .join(
                RoadTypes,
                Roads.type_id == RoadTypes.id
            )
            .where(
                Roads.id == road_id
            )
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response
    
    async def get_road_data(self, road_id: int):
        query_vehicles = (
            select(
                func.count().label('vehicles_count'),
            )
            .select_from(Vehicles)
            .where(Vehicles.road_id == road_id, Vehicles.is_active == True)
        )

        query_cameras = (
            select(
                func.count().label('cameras_count')
            )
            .select_from(Cameras)
            .where(Cameras.roads_id == road_id)
        )

        query_customs_offices = (
            select(
                func.count().label('customs_offices_count')
            )
            .select_from(CustomsOffices)
            .where(CustomsOffices.road_id == road_id)
        )

        vehicles = await self._session.execute(query_vehicles)
        cameras = await self._session.execute(query_cameras)
        customs_offices = await self._session.execute(query_customs_offices)

        response = {'vehicles_count': vehicles.scalar(), 'cameras_count': cameras.scalar(), 'customs_offices_count': customs_offices.scalar()}

        return response

        