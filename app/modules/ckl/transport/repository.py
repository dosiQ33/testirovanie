from sqlalchemy import (
    select,
    func,
)

from app.modules.common.repository import BaseRepository
from ..common.models import (
    Countries
)
from ..infra.models import (
    Roads
)

from .models import (
    Vehicles,
    VehicleTypes,
    TransportCompanies,
    VehicleMakes
)

class VehiclesRepo(BaseRepository):
    model = Vehicles

    async def get_vehicle_info(self, vehicle_id: int):
        query = (
            select(
                Vehicles.number,
                VehicleTypes.name_ru,
                TransportCompanies.name,
                VehicleMakes.name_ru,
                Vehicles.year,
                Countries.name_ru,
                Vehicles.registration_date,
                Vehicles.is_active,
                Vehicles.shape,
                Vehicles.address,
                Roads.name,
                Vehicles.has_customs_booking
            )
            .join(
                VehicleMakes,
                Vehicles.make_id == VehicleMakes.id
            )
            .join(
                TransportCompanies,
                Vehicles.transport_company_id == TransportCompanies.id
            )
            .join(
                VehicleTypes,
                Vehicles.type_id == VehicleTypes.id
            )
            .join(
                Countries,
                Vehicles.country_id == Countries.id
            )
            .join(
                Roads,
                Vehicles.road_id == Roads.id
            )
            .where(
                Vehicles.id == vehicle_id
            )
        )

        result = await self._session.execute(query)
        response =  result.mappings().one_or_none()

        return response