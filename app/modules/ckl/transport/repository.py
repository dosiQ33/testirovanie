from sqlalchemy import select, case, func, distinct

from app.modules.common.repository import BaseRepository
from ..common.models import Countries
from ..infra.models import Roads, RoadTypes

from .models import Vehicles, VehicleTypes, TransportCompanies, VehicleMakes


class VehiclesRepo(BaseRepository):
    model = Vehicles

    async def get_vehicle_info(self, vehicle_id: int):
        query = (
            select(
                Vehicles.number,
                VehicleTypes.name_ru,
                TransportCompanies.name.label('company_name'),
                VehicleMakes.name_ru.label('vehicle_make'),
                Vehicles.year,
                Countries.name_ru.label('registration_country'),
                Vehicles.registration_date,
                Vehicles.is_active,
                Vehicles.address,
                # Roads.name, откоментить когда добавять значение road_id
                Vehicles.has_customs_booking,
            )
            .join(VehicleMakes, Vehicles.make_id == VehicleMakes.id)
            .join(
                TransportCompanies,
                Vehicles.transport_company_id == TransportCompanies.id,
            )
            .join(VehicleTypes, Vehicles.type_id == VehicleTypes.id)
            .join(Countries, Vehicles.country_id == Countries.id)
            # .join(Roads, Vehicles.road_id == Roads.id) откоментить когда добавять значение road_id
            .where(Vehicles.id == vehicle_id)
        )

        result = await self._session.execute(query)
        response = result.mappings().one()

        return response

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