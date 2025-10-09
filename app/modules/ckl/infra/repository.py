from sqlalchemy import select, func

from app.modules.common.repository import BaseRepository

from ..customs.models import CustomsOffices

from .models import (
    Roads,
    RoadTypes,
    Cameras,
    RoadServices
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

class RoadServicesRepo(BaseRepository):
    model = RoadServices

    async def get_road_services_reg_info(self, service_id: int):
        query = (
            select(
                RoadServices.owner_name,
                RoadServices.owner_contact,
                RoadServices.ods_category,
                RoadServices.commissioning_year
            )
            .where(RoadServices.id == service_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response
    
    async def get_road_services_geo_info(self, service_id: int):
        query = (
            select(
                RoadServices.region,
                RoadServices.segment_index,
                Roads.name,
                RoadServices.km_mark,
                RoadServices.placement_side,
                RoadServices.reverse_km_mark
            )
            .join(Roads, RoadServices.road_id == Roads.id)
            .where(RoadServices.id == service_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response
    
    async def get_road_services_infrastructure(self, service_id: int):
        query = (
            select(
                RoadServices.land_allocation,
                RoadServices.engineering_networks,
                RoadServices.exits,
                RoadServices.fuel_station,
                RoadServices.motel,
                RoadServices.toilet,
                RoadServices.food_point,
                RoadServices.retail_point,
                RoadServices.showers,
                RoadServices.service_station,
                RoadServices.car_wash,
                RoadServices.medical_point,
                RoadServices.parking,
                RoadServices.guarded_parking,
                RoadServices.entertainment_zone,
                RoadServices.picnic_area,
                RoadServices.accessible_facilities,
                RoadServices.video_surveillance
            )
            .where(RoadServices.id == service_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response