from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.database.deps import get_session_with_commit
from app.modules.common.router import BaseCRUDRouter, request_key_builder, cache_ttl

from .models import (
    BookingStatuses,
    CargoCustomsDocuments,
    ControlMeasures,
    CustomsBookings,
    CustomsCrossings,
    CustomsDocumentTypes,
    CustomsDocuments,
    CustomsOfficeStatuses,
    CustomsOfficeTypes,
    CustomsOffices,
    CustomsProcedures,
    CustomsSeals,
    DeclarationStatuses,
    DeclarationTypes,
    InspectionResults,
    InspectionTypes,
    Inspections,
    SealStatuses,
    SealTypes,
    SendersRecipients,
    TransitTypes,
    WarehouseTypes,
    CustomsCarriers,
    RepresentOffices
)

from .dtos import (
    BookingStatusesDto,
    CargoCustomsDocumentsDto,
    ControlMeasuresDto,
    CustomsBookingsDto,
    CustomsCrossingsDto,
    CustomsDocumentTypesDto,
    CustomsDocumentsDto,
    CustomsOfficeStatusesDto,
    CustomsOfficeTypesDto,
    CustomsOfficesDto,
    CustomsProceduresDto,
    CustomsSealsDto,
    DeclarationStatusesDto,
    DeclarationTypesDto,
    InspectionResultsDto,
    InspectionTypesDto,
    InspectionsDto,
    SealStatusesDto,
    SealTypesDto,
    SendersRecipientsDto,
    TransitTypesDto,
    WarehouseTypesDto,
    RepresentOfficesDto,
    CustomsCarriersDto
)

from .repository import (
    BookingStatusesRepo,
    CargoCustomsDocumentsRepo,
    ControlMeasuresRepo,
    CustomsBookingsRepo,
    CustomsCrossingsRepo,
    CustomsDocumentTypesRepo,
    CustomsDocumentsRepo,
    CustomsOfficeStatusesRepo,
    CustomsOfficeTypesRepo,
    CustomsOfficesRepo,
    CustomsProceduresRepo,
    CustomsSealsRepo,
    DeclarationStatusesRepo,
    DeclarationTypesRepo,
    InspectionResultsRepo,
    InspectionTypesRepo,
    InspectionsRepo,
    SealStatusesRepo,
    SealTypesRepo,
    SendersRecipientsRepo,
    TransitTypesRepo,
    WarehouseTypesRepo,
    CustomsCarriersRepo,
    RepresentOfficesRepo
)

router = APIRouter(prefix="/customs")


# Simple lookup routers
class BookingStatusesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "booking-statuses", BookingStatuses, BookingStatusesRepo, BookingStatusesDto, tags=["ckl-customs: booking-statuses"]
        )
        self.include_router(self.base_router)


class ControlMeasuresRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "control-measures", ControlMeasures, ControlMeasuresRepo, ControlMeasuresDto, tags=["ckl-customs: control-measures"]
        )
        self.include_router(self.base_router)


class CustomsOfficeStatusesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-office-statuses",
            CustomsOfficeStatuses,
            CustomsOfficeStatusesRepo,
            CustomsOfficeStatusesDto,
            tags=["ckl-customs: customs-office-statuses"],
        )
        self.include_router(self.base_router)


class CustomsOfficeTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-office-types",
            CustomsOfficeTypes,
            CustomsOfficeTypesRepo,
            CustomsOfficeTypesDto,
            tags=["ckl-customs: customs-office-types"],
        )
        self.include_router(self.base_router)


class DeclarationStatusesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "declaration-statuses",
            DeclarationStatuses,
            DeclarationStatusesRepo,
            DeclarationStatusesDto,
            tags=["ckl-customs: declaration-statuses"],
        )
        self.include_router(self.base_router)


class DeclarationTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "declaration-types",
            DeclarationTypes,
            DeclarationTypesRepo,
            DeclarationTypesDto,
            tags=["ckl-customs: declaration-types"],
        )
        self.include_router(self.base_router)


class InspectionResultsRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "inspection-results",
            InspectionResults,
            InspectionResultsRepo,
            InspectionResultsDto,
            tags=["ckl-customs: inspection-results"],
        )
        self.include_router(self.base_router)


class InspectionTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "inspection-types", InspectionTypes, InspectionTypesRepo, InspectionTypesDto, tags=["ckl-customs: inspection-types"]
        )
        self.include_router(self.base_router)


class SealStatusesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "seal-statuses", SealStatuses, SealStatusesRepo, SealStatusesDto, tags=["ckl-customs: seal-statuses"]
        )
        self.include_router(self.base_router)


class SealTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter("seal-types", SealTypes, SealTypesRepo, SealTypesDto, tags=["ckl-customs: seal-types"])
        self.include_router(self.base_router)


class TransitTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "transit-types", TransitTypes, TransitTypesRepo, TransitTypesDto, tags=["ckl-customs: transit-types"]
        )
        self.include_router(self.base_router)


class WarehouseTypesRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "warehouse-types", WarehouseTypes, WarehouseTypesRepo, WarehouseTypesDto, tags=["ckl-customs: warehouse-types"]
        )
        self.include_router(self.base_router)


# Code-based lookup routers with additional endpoints
class CustomsDocumentTypesRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-document-types", tags=["ckl-customs: customs-document-types"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-document-types",
            CustomsDocumentTypes,
            CustomsDocumentTypesRepo,
            CustomsDocumentTypesDto,
            tags=["ckl-customs: customs-document-types"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-code/{code}", response_model=CustomsDocumentTypesDto, summary="Get document type by code")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_code(code: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsDocumentTypesRepo(session).get_by_code(code)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document type not found")
        return CustomsDocumentTypesDto.model_validate(response)


class CustomsProceduresRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-procedures", tags=["ckl-customs: customs-procedures"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-procedures",
            CustomsProcedures,
            CustomsProceduresRepo,
            CustomsProceduresDto,
            tags=["ckl-customs: customs-procedures"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-code/{code}", response_model=CustomsProceduresDto, summary="Get procedure by code")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_code( code: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsProceduresRepo(session).get_by_code(code)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procedure not found")
        return CustomsProceduresDto.model_validate(response)


# Junction table router
class CargoCustomsDocumentsRouter(APIRouter):
    sub_router = APIRouter(prefix="/cargo-customs-documents", tags=["ckl-customs: cargo-customs-documents"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "cargo-customs-documents",
            CargoCustomsDocuments,
            CargoCustomsDocumentsRepo,
            CargoCustomsDocumentsDto,
            tags=["ckl-customs: cargo-customs-documents"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get(
        "/by-cargo/{cargo_id}", response_model=List[CargoCustomsDocumentsDto], summary="Get customs documents by cargo ID"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_cargo_id( cargo_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CargoCustomsDocumentsRepo(session).get_by_cargo_id(cargo_id)
        return [CargoCustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get(
        "/by-document/{document_id}",
        response_model=List[CargoCustomsDocumentsDto],
        summary="Get cargo items by customs document ID",
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_customs_document_id( document_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CargoCustomsDocumentsRepo(session).get_by_customs_document_id(document_id)
        return [CargoCustomsDocumentsDto.model_validate(record) for record in records]


# Complex entity routers with business logic endpoints
class CustomsBookingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-bookings", tags=["ckl-customs: customs-bookings"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-bookings", CustomsBookings, CustomsBookingsRepo, CustomsBookingsDto, tags=["ckl-customs: customs-bookings"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-vehicle/{vehicle_id}", response_model=List[CustomsBookingsDto], summary="Get bookings by vehicle ID")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_bookings_by_vehicle( vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsBookingsRepo(session).get_bookings_by_vehicle(vehicle_id)
        return [CustomsBookingsDto.model_validate(record) for record in records]

    @sub_router.get(
        "/by-office/{office_id}", response_model=List[CustomsBookingsDto], summary="Get bookings by customs office ID"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_bookings_by_customs_office( office_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsBookingsRepo(session).get_bookings_by_customs_office(office_id)
        return [CustomsBookingsDto.model_validate(record) for record in records]

    @sub_router.get("/active", response_model=List[CustomsBookingsDto], summary="Get active bookings requiring inspection")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_active_bookings( session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsBookingsRepo(session).get_active_bookings()
        return [CustomsBookingsDto.model_validate(record) for record in records]

    @sub_router.get("/by-status/{status_id}", response_model=List[CustomsBookingsDto], summary="Get bookings by status")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_bookings_by_status( status_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsBookingsRepo(session).get_bookings_by_status(status_id)
        return [CustomsBookingsDto.model_validate(record) for record in records]


class CustomsCrossingsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-crossings", tags=["ckl-customs: customs-crossings"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-crossings",
            CustomsCrossings,
            CustomsCrossingsRepo,
            CustomsCrossingsDto,
            tags=["ckl-customs: customs-crossings"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-vehicle/{vehicle_id}", response_model=List[CustomsCrossingsDto], summary="Get crossings by vehicle ID")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_crossings_by_vehicle( vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsCrossingsRepo(session).get_crossings_by_vehicle(vehicle_id)
        return [CustomsCrossingsDto.model_validate(record) for record in records]

    @sub_router.get("/recent-entries", response_model=List[CustomsCrossingsDto], summary="Get recent entry crossings")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_recent_entries(
        
        limit: int = Query(50, description="Number of records to return"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        records = await CustomsCrossingsRepo(session).get_recent_entries(limit)
        return [CustomsCrossingsDto.model_validate(record) for record in records]

    @sub_router.get("/recent-exits", response_model=List[CustomsCrossingsDto], summary="Get recent exit crossings")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_recent_exits(
        
        limit: int = Query(50, description="Number of records to return"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        records = await CustomsCrossingsRepo(session).get_recent_exits(limit)
        return [CustomsCrossingsDto.model_validate(record) for record in records]

    @sub_router.get(
        "/requiring-inspection", response_model=List[CustomsCrossingsDto], summary="Get crossings requiring inspection"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_crossings_requiring_inspection( session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsCrossingsRepo(session).get_crossings_requiring_inspection()
        return [CustomsCrossingsDto.model_validate(record) for record in records]


class CustomsDocumentsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-documents", tags=["ckl-customs: customs-documents"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-documents",
            CustomsDocuments,
            CustomsDocumentsRepo,
            CustomsDocumentsDto,
            tags=["ckl-customs: customs-documents"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get(
        "/by-declaration/{declaration_number}", response_model=CustomsDocumentsDto, summary="Get document by declaration number"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_declaration_number( declaration_number: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsDocumentsRepo(session).get_by_declaration_number(declaration_number)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return CustomsDocumentsDto.model_validate(response)

    @sub_router.get("/by-vehicle/{vehicle_id}", response_model=List[CustomsDocumentsDto], summary="Get documents by vehicle ID")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_documents_by_vehicle( vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsDocumentsRepo(session).get_documents_by_vehicle(vehicle_id)
        return [CustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get("/pending-inspections", response_model=List[CustomsDocumentsDto], summary="Get documents pending inspection")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_pending_inspections( session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsDocumentsRepo(session).get_pending_inspections()
        return [CustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get(
        "/by-exporter/{exporter_code}", response_model=List[CustomsDocumentsDto], summary="Get documents by exporter code"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_exporter_code( exporter_code: str, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsDocumentsRepo(session).get_by_exporter_code(exporter_code)
        return [CustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get(
        "/by-importer/{importer_code}", response_model=List[CustomsDocumentsDto], summary="Get documents by importer code"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_importer_code( importer_code: str, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsDocumentsRepo(session).get_by_importer_code(importer_code)
        return [CustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get("/transit", response_model=List[CustomsDocumentsDto], summary="Get transit documents")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_transit_documents(
        
        transit_type_id: int = Query(None, description="Filter by transit type ID"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        records = await CustomsDocumentsRepo(session).get_transit_documents(transit_type_id)
        return [CustomsDocumentsDto.model_validate(record) for record in records]

    @sub_router.get("/by-office/{office_id}", response_model=List[CustomsDocumentsDto], summary="Get documents by customs office")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_documents_by_customs_office( office_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsDocumentsRepo(session).get_documents_by_customs_office(office_id)
        return [CustomsDocumentsDto.model_validate(record) for record in records]


class CustomsOfficesRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-offices", tags=["ckl-customs: customs-offices"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-offices", CustomsOffices, CustomsOfficesRepo, CustomsOfficesDto, tags=["ckl-customs: customs-offices"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-code/{code}", response_model=CustomsOfficesDto, summary="Get customs office by code")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_code( code: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsOfficesRepo(session).get_by_code(code)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customs office not found")
        return CustomsOfficesDto.model_validate(response)

    @sub_router.get("/border-points", response_model=List[CustomsOfficesDto], summary="Get border point offices")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_border_points( session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsOfficesRepo(session).get_border_points()
        return [CustomsOfficesDto.model_validate(record) for record in records]

    @sub_router.get("/by-region/{kato_code}", response_model=List[CustomsOfficesDto], summary="Get offices by KATO region code")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_region( kato_code: str, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsOfficesRepo(session).get_by_region(kato_code)
        return [CustomsOfficesDto.model_validate(record) for record in records]

    @sub_router.get("/active", response_model=List[CustomsOfficesDto], summary="Get active customs offices")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_active_offices( session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsOfficesRepo(session).get_active_offices()
        return [CustomsOfficesDto.model_validate(record) for record in records]


class CustomsSealsRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-seals", tags=["ckl-customs: customs-seals"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-seals", CustomsSeals, CustomsSealsRepo, CustomsSealsDto, tags=["ckl-customs: customs-seals"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-number/{number}", response_model=CustomsSealsDto, summary="Get seal by number")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_number( number: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsSealsRepo(session).get_by_number(number)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seal not found")
        return CustomsSealsDto.model_validate(response)

    @sub_router.get(
        "/active-by-vehicle/{vehicle_id}", response_model=List[CustomsSealsDto], summary="Get active seals by vehicle ID"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_active_seals_by_vehicle( vehicle_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsSealsRepo(session).get_active_seals_by_vehicle(vehicle_id)
        return [CustomsSealsDto.model_validate(record) for record in records]

    @sub_router.get("/by-office/{office_id}", response_model=List[CustomsSealsDto], summary="Get seals by customs office ID")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_seals_by_customs_office( office_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await CustomsSealsRepo(session).get_seals_by_customs_office(office_id)
        return [CustomsSealsDto.model_validate(record) for record in records]


class InspectionsRouter(APIRouter):
    sub_router = APIRouter(prefix="/inspections", tags=["ckl-customs: inspections"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "inspections", Inspections, InspectionsRepo, InspectionsDto, tags=["ckl-customs: inspections"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get(
        "/by-inspector/{inspector_name}", response_model=List[InspectionsDto], summary="Get inspections by inspector name"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_inspector( inspector_name: str, session: AsyncSession = Depends(get_session_with_commit)):
        records = await InspectionsRepo(session).get_by_inspector(inspector_name)
        return [InspectionsDto.model_validate(record) for record in records]

    @sub_router.get("/pending", response_model=List[InspectionsDto], summary="Get pending inspections")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_pending_inspections( session: AsyncSession = Depends(get_session_with_commit)):
        records = await InspectionsRepo(session).get_pending_inspections()
        return [InspectionsDto.model_validate(record) for record in records]

    @sub_router.get("/by-type/{type_id}", response_model=List[InspectionsDto], summary="Get inspections by type")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_type( type_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await InspectionsRepo(session).get_by_type(type_id)
        return [InspectionsDto.model_validate(record) for record in records]

    @sub_router.get("/by-result/{result_id}", response_model=List[InspectionsDto], summary="Get inspections by result")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_result( result_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await InspectionsRepo(session).get_by_result(result_id)
        return [InspectionsDto.model_validate(record) for record in records]


class SendersRecipientsRouter(APIRouter):
    sub_router = APIRouter(prefix="/senders-recipients", tags=["ckl-customs: senders-recipients"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "senders-recipients",
            SendersRecipients,
            SendersRecipientsRepo,
            SendersRecipientsDto,
            tags=["ckl-customs: senders-recipients"],
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/by-iin-bin/{iin_bin}", response_model=SendersRecipientsDto, summary="Get sender/recipient by IIN/BIN")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_iin_bin( iin_bin: str, session: AsyncSession = Depends(get_session_with_commit)):
        response = await SendersRecipientsRepo(session).get_by_iin_bin(iin_bin)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return SendersRecipientsDto.model_validate(response)

    @sub_router.get(
        "/by-organization/{organization_id}", response_model=List[SendersRecipientsDto], summary="Get entities by organization ID"
    )
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_organization_id( organization_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await SendersRecipientsRepo(session).get_by_organization_id(organization_id)
        return [SendersRecipientsDto.model_validate(record) for record in records]

    @sub_router.get("/foreign", response_model=List[SendersRecipientsDto], summary="Get foreign entities")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_foreign_entities( session: AsyncSession = Depends(get_session_with_commit)):
        records = await SendersRecipientsRepo(session).get_foreign_entities()
        return [SendersRecipientsDto.model_validate(record) for record in records]

    @sub_router.get("/domestic", response_model=List[SendersRecipientsDto], summary="Get domestic entities")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_domestic_entities( session: AsyncSession = Depends(get_session_with_commit)):
        records = await SendersRecipientsRepo(session).get_domestic_entities()
        return [SendersRecipientsDto.model_validate(record) for record in records]

    @sub_router.get("/active", response_model=List[SendersRecipientsDto], summary="Get active entities")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_active_entities(session: AsyncSession = Depends(get_session_with_commit)):
        records = await SendersRecipientsRepo(session).get_active_entities()
        return [SendersRecipientsDto.model_validate(record) for record in records]

    @sub_router.get("/by-country/{country_id}", response_model=List[SendersRecipientsDto], summary="Get entities by country")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_by_country(country_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        records = await SendersRecipientsRepo(session).get_by_country(country_id)
        return [SendersRecipientsDto.model_validate(record) for record in records]

    @sub_router.get("/search", response_model=List[SendersRecipientsDto], summary="Search entities by name")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def search_by_name(
        name_pattern: str = Query(..., description="Name pattern to search for"),
        session: AsyncSession = Depends(get_session_with_commit),
    ):
        records = await SendersRecipientsRepo(session).search_by_name(name_pattern)
        return [SendersRecipientsDto.model_validate(record) for record in records]


class CustomsCarriersRouter(APIRouter):
    sub_router = APIRouter(prefix="/customs-carriers", tags=["ckl-customs: customs-carriers"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "customs-carriers", CustomsCarriers, CustomsCarriersRepo, CustomsCarriersDto, tags=["ckl-customs: customs-carriers"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{customs_id}",)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(customs_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        response = await CustomsCarriersRepo(session).get_base_info(customs_id)

        return response
        
class RepresentOfficesRouter(APIRouter):
    sub_router = APIRouter(prefix="/represent-offices", tags=["ckl-customs: represent-offices"])

    def __init__(self):
        super().__init__()
        self.base_router = BaseCRUDRouter(
            "represent-offices", RepresentOffices, RepresentOfficesRepo, RepresentOfficesDto, tags=["ckl-customs: represent-offices"]
        )
        self.include_router(self.sub_router)
        self.include_router(self.base_router)

    @sub_router.get("/info/{office_id}",)
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_info(office_id: int, session: AsyncSession = Depends(get_session_with_commit)):
        response = await RepresentOfficesRepo(session).get_base_info(office_id)

        return response

# Include all routers
router.include_router(BookingStatusesRouter())
router.include_router(ControlMeasuresRouter())
router.include_router(CustomsOfficeStatusesRouter())
router.include_router(CustomsOfficeTypesRouter())
router.include_router(DeclarationStatusesRouter())
router.include_router(DeclarationTypesRouter())
router.include_router(InspectionResultsRouter())
router.include_router(InspectionTypesRouter())
router.include_router(SealStatusesRouter())
router.include_router(SealTypesRouter())
router.include_router(TransitTypesRouter())
router.include_router(WarehouseTypesRouter())
router.include_router(CustomsDocumentTypesRouter())
router.include_router(CustomsProceduresRouter())
router.include_router(CargoCustomsDocumentsRouter())
router.include_router(CustomsBookingsRouter())
router.include_router(CustomsCrossingsRouter())
router.include_router(CustomsDocumentsRouter())
router.include_router(CustomsOfficesRouter())
router.include_router(CustomsSealsRouter())
router.include_router(InspectionsRouter())
router.include_router(SendersRecipientsRouter())
router.include_router(CustomsCarriersRouter())
router.include_router(RepresentOfficesRouter())
