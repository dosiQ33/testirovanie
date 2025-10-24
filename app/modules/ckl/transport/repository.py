from sqlalchemy import select, case, func, distinct
from geoalchemy2.functions import ST_Covers, ST_SetSRID

from app.modules.common.repository import BaseRepository
from ..common.models import Countries
from ..infra.models import Roads, CameraEvents
from ..customs.models import (
    CustomsBookings,
    BookingStatuses,
    CustomsOffices,
    CustomsCrossings,
    WarehouseTypes
)

from ...ext.kazgeodesy.models import KazgeodesyRkOblasti, KazgeodesyRkRaiony
from ...common.utils import territory_to_geo_element


from .models import (
    Vehicles, 
    VehicleTypes, 
    TransportCompanies, 
    VehicleMakes,
    Trailers,
    Warehouses,
)


class VehiclesRepo(BaseRepository):
    model = Vehicles

    async def get_vehicle_info(self, vehicle_id: int):
        query = (
            select(
                Vehicles.number,
                VehicleTypes.name_ru.label('vehicle_type'),
                TransportCompanies.name.label('company_name'),
                VehicleMakes.name_ru.label('vehicle_make'),
                Vehicles.year,
                Vehicles.registration_date,
                Countries.name_ru.label('registration_country'),
                Vehicles.is_active,
                Roads.name,
                # Trailers.number откоментить когда заполнят trailers
            )
            .join(VehicleMakes, Vehicles.make_id == VehicleMakes.id)
            .join(
                TransportCompanies,
                Vehicles.transport_company_id == TransportCompanies.id,
            )
            .join(VehicleTypes, Vehicles.type_id == VehicleTypes.id)
            .join(Countries, Vehicles.country_id == Countries.id)
            .join(Roads, Vehicles.road_id == Roads.id)
            # .outerjoin(Trailers, Trailers.vehicle_id == Vehicles.id) откоментить когда заполнят trailers
            .where(Vehicles.id == vehicle_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response
    
    async def get_vehicle_position_info(self, vehicle_id: int):
        vehicle_shape_sq = (
            select(ST_SetSRID(Vehicles.shape, 4326))
            .where(Vehicles.id == vehicle_id)
            .scalar_subquery()
        )

        query_location = (
            select(
                KazgeodesyRkRaiony.name_ru.label('raion'),
                KazgeodesyRkOblasti.name_ru.label('oblast')
            )
            .join(KazgeodesyRkOblasti, KazgeodesyRkOblasti.id == KazgeodesyRkRaiony.parent_id)
            .where(ST_Covers(KazgeodesyRkRaiony.geom, vehicle_shape_sq))
        )

        last_cam_ts = (
            select(func.max(CameraEvents.event_timestamp))
            .where(CameraEvents.vehicle_id == vehicle_id)
            .scalar_subquery()
        )

        last_booking = (
            select(
                Roads.name.label("road_name"),
                CustomsBookings.preferred_entry_timestamp.label("date_of_booking"),
                CustomsOffices.name_ru.label("customs_office_name"),
            )
            .join(Vehicles, CustomsBookings.vehicle_id == Vehicles.id)
            .join(Roads, Vehicles.road_id == Roads.id)
            .join(CustomsOffices, CustomsOffices.id == CustomsBookings.customs_office_id)
            .where(
                Vehicles.id == vehicle_id,
                CustomsBookings.vehicle_id == vehicle_id,
                CustomsBookings.status_id.in_([1, 2]),
            )
            .order_by(CustomsBookings.preferred_entry_timestamp.desc())
            .limit(1)
            .subquery()
        )

        query_info = (
            select(
                last_cam_ts.label("last_event_timestamp"),
                last_booking.c.road_name,
                last_booking.c.date_of_booking,
                last_booking.c.customs_office_name,
            )
        )

        result_location = await self._session.execute(query_location)
        response_location = result_location.mappings().one()

        result_info = await self._session.execute(query_info)
        response_info = result_info.mappings().one()

        return {'raion': response_location['raion'], 'oblast':response_location['oblast'], **response_info}
    

    async def get_entrypoints(self, vehicle_id: int):
        query_entry = (
            select(
                CustomsOffices.name_ru,
                func.ST_AsGeoJSON(func.ST_Transform(CustomsOffices.shape, 4326)).label("shape")
            )
            .join(CustomsCrossings, CustomsOffices.id == CustomsCrossings.customs_offices_id)
            .where(CustomsCrossings.is_entry == True, CustomsCrossings.vehicle_id == vehicle_id)
            .order_by(CustomsCrossings.timestamp.desc())
            .limit(1)
        )

        query_out = (
            select(
                CustomsOffices.name_ru,
                func.ST_AsGeoJSON(func.ST_Transform(CustomsOffices.shape, 4326)).label("shape")
            )
            .join(CustomsCrossings, CustomsOffices.id == CustomsCrossings.customs_offices_id)
            .where(CustomsCrossings.is_entry == False, CustomsCrossings.vehicle_id == vehicle_id)
            .order_by(CustomsCrossings.timestamp.desc())
            .limit(1)
        )

        result_entry = await self._session.execute(query_entry)
        response_entry = result_entry.mappings().one()

        result_out = await self._session.execute(query_out)
        response_out = result_out.mappings().one()

        return {'shape_entry': response_entry['shape'], 'shape_out': response_out['shape']}
    
    async def get_intermediate_points(self, vehicle_id: int):
        entry_ts_sq = (
            select(func.max(CustomsCrossings.timestamp))
            .where(
                CustomsCrossings.vehicle_id == vehicle_id,
                CustomsCrossings.is_entry.is_(True),
            )
            .scalar_subquery()
        )
        exit_ts_sq = (
            select(func.min(CustomsCrossings.timestamp))
            .where(
                CustomsCrossings.vehicle_id == vehicle_id,
                CustomsCrossings.is_entry.is_(False),
                CustomsCrossings.timestamp > entry_ts_sq,
            )
            .scalar_subquery()
        )

        end_bound = func.coalesce(exit_ts_sq, func.now())

        query = (
            select(
                CameraEvents.id,
                func.ST_AsGeoJSON(CameraEvents.shape).label("shape"),
                CameraEvents.event_timestamp,
            )
            .where(
                CameraEvents.vehicle_id == vehicle_id,
                CameraEvents.event_timestamp >= entry_ts_sq,
                CameraEvents.event_timestamp < end_bound,
            )
            .order_by(CameraEvents.event_timestamp.asc())
        )

        result = await self._session.execute(query)
        rows = result.all()

        return [dict(row._mapping) for row in rows]
        

class TransportCompaniesRepo(BaseRepository):
    model = TransportCompanies

    async def get_base_info(self, company_id: int):
        query = (
            select(
                TransportCompanies.name,
                case((TransportCompanies.is_international == False, TransportCompanies.bin), else_=None).label('bin'),
                case((TransportCompanies.is_international == True, TransportCompanies.vat_number), else_=None).label('vat_number'),
                TransportCompanies.registration_number,
                TransportCompanies.address,
                TransportCompanies.phone,
                TransportCompanies.email,
                TransportCompanies.contact_person
            )
            .where(TransportCompanies.id == company_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response

    async def get_transport_info(self, company_id: int):
        total_subq = (
            select(func.count(distinct(Vehicles.id)))
            .where(Vehicles.transport_company_id == company_id)
            .scalar_subquery()
        )

        active_subq = (
            select(func.count(distinct(Vehicles.id)))
            .where(
                Vehicles.transport_company_id == company_id,
                Vehicles.is_active.is_(True),
            )
            .scalar_subquery()
        )

        query = select(
            total_subq.label("vehicles_total"),
            active_subq.label("vehicles_in_kz"),
        )


        result = await self._session.execute(query)
        response = result.mappings().one()

        return response
    
    async def get_all_transport_comapnies(self):
        query = (
            select(
                TransportCompanies.id,
                TransportCompanies.name,
                TransportCompanies.is_international,
                TransportCompanies.bin,
                TransportCompanies.vat_number,
                TransportCompanies.registration_number,
                TransportCompanies.address,
                func.count(Vehicles.id).label('vehicles_count')
            )
            .outerjoin(Vehicles, Vehicles.transport_company_id == TransportCompanies.id)
            .group_by(
                TransportCompanies.id,
                TransportCompanies.name,
                TransportCompanies.is_international,
                TransportCompanies.bin,
                TransportCompanies.vat_number,
                TransportCompanies.registration_number,
                TransportCompanies.address,
            )
        )

        result = await self._session.execute(query)
        rows = result.all()

        return [dict(row._mapping) for row in rows]
    

class WarehousesRepository(BaseRepository):
    model = Warehouses

    async def get_warehouse_info(self, warehouse_id: int):
        query = (
            select(
                Warehouses.address,
                Warehouses.contact_person,
                Warehouses.contact_information,
                Warehouses.iin_bin,
                Warehouses.date_start,
                Warehouses.capacity,
                WarehouseTypes.name_ru.label('type_name'),
                CustomsOffices.name_ru.label('custom_office_name'),
                Warehouses.other_information
            )
            .join(WarehouseTypes, Warehouses.type_id == WarehouseTypes.id)
            .join(CustomsOffices, Warehouses.customs_offices_id == CustomsOffices.id)
            .where(Warehouses.id == warehouse_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response