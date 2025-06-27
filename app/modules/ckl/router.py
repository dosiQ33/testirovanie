"""
Project: nam
Created Date: Wednesday January 29th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from fastapi import APIRouter

from app.modules.common.router import BaseCRUDRouter
from .filters import (
    CountriesFilter,
    CustomsOfficesFilter,
    CustomsProceduresFilter,
    CustomsPointsFilter,
    TransportCompaniesFilter,
    VehicleTypesFilter,
    VehicleMakeTypesFilter,
    VehiclesFilter,
    BookingStatusesFilter,
    BookingsFilter,
    CameraTypesFilter,
    CamerasFilter,
    CameraEventsFilter,
    WeightingStationsFilter,
    WeightingEventsFilter,
    SendersFilter,
    ReceiversFilter,
    CustomsDeclarationsFilter,
    InspectionsFilter,
    CargoTypesFilter,
    PackageTypesFilter,
    CargosFilter,
    CargoItemsFilter,
    VehicleRouteTrackingsFilter,
    VehicleCustomsCrossingsFilter,
    WarehousesFilter,
    DeclarationTypesFilter,
    DeclarationStatusesFilter,
    PackagingTypesFilter,
    ParticipantRolesFilter,
)
from .dtos import (
    CustomsPointsDto,
    TransportCompaniesDto,
    VehicleTypesDto,
    VehiclesDto,
    CameraTypesDto,
    CamerasDto,
    CameraEventsDto,
    WeightingStationsDto,
    WeightingEventsDto,
    SendersDto,
    ReceiversDto,
    CargosDto,
    CargoItemsDto,
    VehicleRouteTrackingsDto,
    VehicleCustomsCrossingsDto,
    WarehousesDto,
    InspectionsDto,
    CargoTypesDto,
    PackageTypesDto,
    CustomsDeclarationsDto,
    CountriesDto,
    CustomsOfficesDto,
    CustomsProceduresDto,
    VehicleMakeTypesDto,
    BookingStatusesDto,
    BookingsDto,
    DeclarationTypesDto,
    DeclarationStatusesDto,
    PackagingTypesDto,
    ParticipantRolesDto,
)
from .repository import (
    CustomsPointsRepo,
    TransportCompaniesRepo,
    VehicleTypesRepo,
    VehiclesRepo,
    CameraTypesRepo,
    CamerasRepo,
    CameraEventsRepo,
    WeightingStationsRepo,
    WeightingEventsRepo,
    SendersRepo,
    ReceiversRepo,
    CargosRepo,
    CargoItemsRepo,
    VehicleRouteTrackingsRepo,
    VehicleCustomsCrossingsRepo,
    WarehousesRepo,
    InspectionsRepo,
    CargoTypesRepo,
    PackageTypesRepo,
    CustomsDeclarationsRepo,
    CountriesRepo,
    CustomsOfficesRepo,
    CustomsProceduresRepo,
    VehicleMakeTypesRepo,
    BookingStatusesRepo,
    BookingsRepo,
    DeclarationTypesRepo,
    DeclarationStatusesRepo,
    PackagingTypesRepo,
    ParticipantRolesRepo,
)
from .models import (
    CustomsPoints,
    TransportCompanies,
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
    Countries,
    CustomsOffices,
    CustomsProcedures,
    VehicleMakeTypes,
    BookingStatuses,
    Bookings,
    DeclarationTypes,
    DeclarationStatuses,
    PackagingTypes,
    ParticipantRoles,
)


router = APIRouter(prefix="/ckl")


class CustomsPointsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-points", tags=["ckl: customs-points"])
    base_router = BaseCRUDRouter(
        "customs-points",
        CustomsPoints,
        CustomsPointsRepo,
        CustomsPointsDto,
        CustomsPointsFilter,
        tags=["ckl: customs-points"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class TransportCompaniesRouter(APIRouter):
    sub_router = APIRouter(prefix="/transport-companies", tags=["ckl: transport-companies"])
    base_router = BaseCRUDRouter(
        "transport-companies",
        TransportCompanies,
        TransportCompaniesRepo,
        TransportCompaniesDto,
        TransportCompaniesFilter,
        tags=["ckl: transport-companies"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class VehicleTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicle-types", tags=["ckl: vehicle-types"])
    base_router = BaseCRUDRouter(
        "vehicle-types",
        VehicleTypes,
        VehicleTypesRepo,
        VehicleTypesDto,
        VehicleTypesFilter,
        tags=["ckl: vehicle-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class VehiclesRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicles", tags=["ckl: vehicles"])
    base_router = BaseCRUDRouter(
        "vehicles",
        Vehicles,
        VehiclesRepo,
        VehiclesDto,
        VehiclesFilter,
        tags=["ckl: vehicles"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CameraTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/camera-types", tags=["ckl: camera-types"])
    base_router = BaseCRUDRouter(
        "camera-types",
        CameraTypes,
        CameraTypesRepo,
        CameraTypesDto,
        CameraTypesFilter,
        tags=["ckl: camera-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CamerasRouter(APIRouter):
    sub_router = APIRouter(prefix="/cameras", tags=["ckl: cameras"])
    base_router = BaseCRUDRouter(
        "cameras",
        Cameras,
        CamerasRepo,
        CamerasDto,
        CamerasFilter,
        tags=["ckl: cameras"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CameraEventsRouter(APIRouter):
    sub_router = APIRouter(prefix="/camera-events", tags=["ckl: camera-events"])
    base_router = BaseCRUDRouter(
        "camera-events",
        CameraEvents,
        CameraEventsRepo,
        CameraEventsDto,
        CameraEventsFilter,
        tags=["ckl: camera-events"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class WeightingStationsRouter(APIRouter):
    sub_router = APIRouter(prefix="/weighting-stations", tags=["ckl: weighting-stations"])
    base_router = BaseCRUDRouter(
        "weighting-stations",
        WeightingStations,
        WeightingStationsRepo,
        WeightingStationsDto,
        WeightingStationsFilter,
        tags=["ckl: weighting-stations"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class WeightingEventsRouter(APIRouter):
    sub_router = APIRouter(prefix="/weighting-events", tags=["ckl: weighting-events"])
    base_router = BaseCRUDRouter(
        "weighting-events",
        WeightingEvents,
        WeightingEventsRepo,
        WeightingEventsDto,
        WeightingEventsFilter,
        tags=["ckl: weighting-events"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class SendersRouter(APIRouter):
    sub_router = APIRouter(prefix="/senders", tags=["ckl: senders"])
    base_router = BaseCRUDRouter(
        "senders",
        Senders,
        SendersRepo,
        SendersDto,
        SendersFilter,
        tags=["ckl: senders"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class ReceiversRouter(APIRouter):
    sub_router = APIRouter(prefix="/receivers", tags=["ckl: receivers"])
    base_router = BaseCRUDRouter(
        "receivers",
        Receivers,
        ReceiversRepo,
        ReceiversDto,
        ReceiversFilter,
        tags=["ckl: receivers"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CargosRouter(APIRouter):
    sub_router = APIRouter(prefix="/cargos", tags=["ckl: cargos"])
    base_router = BaseCRUDRouter(
        "cargos",
        Cargos,
        CargosRepo,
        CargosDto,
        CargosFilter,
        tags=["ckl: cargos"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CargoItemsRouter(APIRouter):
    sub_router = APIRouter(prefix="/cargo-items", tags=["ckl: cargo-items"])
    base_router = BaseCRUDRouter(
        "cargo-items",
        CargoItems,
        CargoItemsRepo,
        CargoItemsDto,
        CargoItemsFilter,
        tags=["ckl: cargo-items"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class VehicleRouteTrackingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicle-route-trackings", tags=["ckl: vehicle-route-trackings"])
    base_router = BaseCRUDRouter(
        "vehicle-route-trackings",
        VehicleRouteTrackings,
        VehicleRouteTrackingsRepo,
        VehicleRouteTrackingsDto,
        VehicleRouteTrackingsFilter,
        tags=["ckl: vehicle-route-trackings"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class VehicleCustomsCrossingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicle-customs-crossings", tags=["ckl: vehicle-customs-crossings"])
    base_router = BaseCRUDRouter(
        "vehicle-customs-crossings",
        VehicleCustomsCrossings,
        VehicleCustomsCrossingsRepo,
        VehicleCustomsCrossingsDto,
        VehicleCustomsCrossingsFilter,
        tags=["ckl: vehicle-customs-crossings"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class WarehousesRouter(APIRouter):
    sub_router = APIRouter(prefix="/warehouses", tags=["ckl: warehouses"])
    base_router = BaseCRUDRouter(
        "warehouses",
        Warehouses,
        WarehousesRepo,
        WarehousesDto,
        WarehousesFilter,
        tags=["ckl: warehouses"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class InspectionsRouter(APIRouter):
    sub_router = APIRouter(prefix="/inspections", tags=["ckl: inspections"])
    base_router = BaseCRUDRouter(
        "inspections",
        Inspections,
        InspectionsRepo,
        InspectionsDto,
        InspectionsFilter,
        tags=["ckl: inspections"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CargoTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/cargo-types", tags=["ckl: cargo-types"])
    base_router = BaseCRUDRouter(
        "cargo-types",
        CargoTypes,
        CargoTypesRepo,
        CargoTypesDto,
        CargoTypesFilter,
        tags=["ckl: cargo-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class PackageTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/package-types", tags=["ckl: package-types"])
    base_router = BaseCRUDRouter(
        "package-types",
        PackageTypes,
        PackageTypesRepo,
        PackageTypesDto,
        PackageTypesFilter,
        tags=["ckl: package-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CustomsDeclarationsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-declarations", tags=["ckl: customs-declarations"])
    base_router = BaseCRUDRouter(
        "customs-declarations",
        CustomsDeclarations,
        CustomsDeclarationsRepo,
        CustomsDeclarationsDto,
        CustomsDeclarationsFilter,
        tags=["ckl: customs-declarations"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CountriesRouter(APIRouter):
    sub_router = APIRouter(prefix="/countries", tags=["ckl: countries"])
    base_router = BaseCRUDRouter(
        "countries",
        Countries,
        CountriesRepo,
        CountriesDto,
        CountriesFilter,
        tags=["ckl: countries"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CustomsOfficesRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-offices", tags=["ckl: customs-offices"])
    base_router = BaseCRUDRouter(
        "customs-offices",
        CustomsOffices,
        CustomsOfficesRepo,
        CustomsOfficesDto,
        CustomsOfficesFilter,
        tags=["ckl: customs-offices"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class CustomsProceduresRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-procedures", tags=["ckl: customs-procedures"])
    base_router = BaseCRUDRouter(
        "customs-procedures",
        CustomsProcedures,
        CustomsProceduresRepo,
        CustomsProceduresDto,
        CustomsProceduresFilter,
        tags=["ckl: customs-procedures"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class VehicleMakeTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/vehicle-make-types", tags=["ckl: vehicle-make-types"])
    base_router = BaseCRUDRouter(
        "vehicle-make-types",
        VehicleMakeTypes,
        VehicleMakeTypesRepo,
        VehicleMakeTypesDto,
        VehicleMakeTypesFilter,
        tags=["ckl: vehicle-make-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class BookingStatusesRouter(APIRouter):
    sub_router = APIRouter(prefix="/booking-statuses", tags=["ckl: booking-statuses"])
    base_router = BaseCRUDRouter(
        "booking-statuses",
        BookingStatuses,
        BookingStatusesRepo,
        BookingStatusesDto,
        BookingStatusesFilter,
        tags=["ckl: booking-statuses"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class BookingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/bookings", tags=["ckl: bookings"])
    base_router = BaseCRUDRouter(
        "bookings",
        Bookings,
        BookingsRepo,
        BookingsDto,
        BookingsFilter,
        tags=["ckl: bookings"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class DeclarationTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/declaration-types", tags=["ckl: declaration-types"])
    base_router = BaseCRUDRouter(
        "declaration-types",
        DeclarationTypes,
        DeclarationTypesRepo,
        DeclarationTypesDto,
        DeclarationTypesFilter,
        tags=["ckl: declaration-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class DeclarationStatusesRouter(APIRouter):
    sub_router = APIRouter(prefix="/declaration-statuses", tags=["ckl: declaration-statuses"])
    base_router = BaseCRUDRouter(
        "declaration-statuses",
        DeclarationStatuses,
        DeclarationStatusesRepo,
        DeclarationStatusesDto,
        DeclarationStatusesFilter,
        tags=["ckl: declaration-statuses"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class PackagingTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/packaging-types", tags=["ckl: packaging-types"])
    base_router = BaseCRUDRouter(
        "packaging-types",
        PackagingTypes,
        PackagingTypesRepo,
        PackagingTypesDto,
        PackagingTypesFilter,
        tags=["ckl: packaging-types"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


class ParticipantRolesRouter(APIRouter):
    sub_router = APIRouter(prefix="/participant-roles", tags=["ckl: participant-roles"])
    base_router = BaseCRUDRouter(
        "participant-roles",
        ParticipantRoles,
        ParticipantRolesRepo,
        ParticipantRolesDto,
        ParticipantRolesFilter,
        tags=["ckl: participant-roles"],
    )

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)
        self.include_router(self.base_router)


# Include all routers
router.include_router(CustomsPointsRouter())
router.include_router(TransportCompaniesRouter())
router.include_router(VehicleTypesRouter())
router.include_router(VehiclesRouter())
router.include_router(CameraTypesRouter())
router.include_router(CamerasRouter())
router.include_router(CameraEventsRouter())
router.include_router(WeightingStationsRouter())
router.include_router(WeightingEventsRouter())
router.include_router(SendersRouter())
router.include_router(ReceiversRouter())
router.include_router(CargosRouter())
router.include_router(CargoItemsRouter())
router.include_router(VehicleRouteTrackingsRouter())
router.include_router(VehicleCustomsCrossingsRouter())
router.include_router(WarehousesRouter())
router.include_router(InspectionsRouter())
router.include_router(CargoTypesRouter())
router.include_router(PackageTypesRouter())
router.include_router(CustomsDeclarationsRouter())
router.include_router(CountriesRouter())
router.include_router(CustomsOfficesRouter())
router.include_router(CustomsProceduresRouter())
router.include_router(VehicleMakeTypesRouter())
router.include_router(BookingStatusesRouter())
router.include_router(BookingsRouter())
router.include_router(DeclarationTypesRouter())
router.include_router(DeclarationStatusesRouter())
router.include_router(PackagingTypesRouter())
router.include_router(ParticipantRolesRouter())
