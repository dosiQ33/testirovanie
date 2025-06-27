"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from app.modules.common.repository import BaseRepository
from .models import (
    BookingStatuses,
    Bookings,
    Countries,
    CustomsOffices,
    CustomsProcedures,
    DeclarationTypes,
    PackagingTypes,
    ParticipantRoles,
    DeclarationStatuses,
    CustomsPoints,
    TransportCompanies,
    VehicleMakeTypes,
    VehicleTypes,
    Vehicles,
    CameraTypes,
    Cameras,
    CameraEvents,
    WeightingStations,
    WeightingEvents,
    Senders,
    Receivers,
    Cargos,
    CargoItems,
    VehicleRouteTrackings,
    VehicleCustomsCrossings,
    Warehouses,
    Inspections,
    CargoTypes,
    PackageTypes,
    CustomsDeclarations,
)


class CountriesRepo(BaseRepository):
    model = Countries


class DeclarationTypesRepo(BaseRepository):
    model = DeclarationTypes


class PackagingTypesRepo(BaseRepository):
    model = PackagingTypes


class ParticipantRolesRepo(BaseRepository):
    model = ParticipantRoles


class DeclarationStatusesRepo(BaseRepository):
    model = DeclarationStatuses


class BookingsRepo(BaseRepository):
    model = Bookings


class BookingStatusesRepo(BaseRepository):
    model = BookingStatuses


class CustomsOfficesRepo(BaseRepository):
    model = CustomsOffices


class CustomsProceduresRepo(BaseRepository):
    model = CustomsProcedures


class VehicleMakeTypesRepo(BaseRepository):
    model = VehicleMakeTypes


class StatusesRepo(BaseRepository):
    model = DeclarationStatuses


class CustomsPointsRepo(BaseRepository):
    model = CustomsPoints


class TransportCompaniesRepo(BaseRepository):
    model = TransportCompanies


class VehicleTypesRepo(BaseRepository):
    model = VehicleTypes


class VehiclesRepo(BaseRepository):
    model = Vehicles


class CameraTypesRepo(BaseRepository):
    model = CameraTypes


class CamerasRepo(BaseRepository):
    model = Cameras


class CameraEventsRepo(BaseRepository):
    model = CameraEvents


class WeightingStationsRepo(BaseRepository):
    model = WeightingStations


class WeightingEventsRepo(BaseRepository):
    model = WeightingEvents


class SendersRepo(BaseRepository):
    model = Senders


class ReceiversRepo(BaseRepository):
    model = Receivers


class CargosRepo(BaseRepository):
    model = Cargos


class CargoItemsRepo(BaseRepository):
    model = CargoItems


class VehicleRouteTrackingsRepo(BaseRepository):
    model = VehicleRouteTrackings


class VehicleCustomsCrossingsRepo(BaseRepository):
    model = VehicleCustomsCrossings


class WarehousesRepo(BaseRepository):
    model = Warehouses


class InspectionsRepo(BaseRepository):
    model = Inspections


class CargoTypesRepo(BaseRepository):
    model = CargoTypes


class PackageTypesRepo(BaseRepository):
    model = PackageTypes


class CustomsDeclarationsRepo(BaseRepository):
    model = CustomsDeclarations
