from sqlalchemy import select

from app.modules.common.repository import BaseRepository

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

from ..common.models import (
    TnVed
)

from ..cargo.models import (
    Cargos
)

from app.modules.ckf.models import Organizations, Okeds, TaxRegimes

# Simple lookup repositories
class BookingStatusesRepo(BaseRepository):
    model = BookingStatuses


class ControlMeasuresRepo(BaseRepository):
    model = ControlMeasures


class CustomsOfficeStatusesRepo(BaseRepository):
    model = CustomsOfficeStatuses


class CustomsOfficeTypesRepo(BaseRepository):
    model = CustomsOfficeTypes


class DeclarationStatusesRepo(BaseRepository):
    model = DeclarationStatuses


class DeclarationTypesRepo(BaseRepository):
    model = DeclarationTypes


class InspectionResultsRepo(BaseRepository):
    model = InspectionResults


class InspectionTypesRepo(BaseRepository):
    model = InspectionTypes


class SealStatusesRepo(BaseRepository):
    model = SealStatuses


class SealTypesRepo(BaseRepository):
    model = SealTypes


class TransitTypesRepo(BaseRepository):
    model = TransitTypes


class WarehouseTypesRepo(BaseRepository):
    model = WarehouseTypes


# Code-based lookup repositories
class CustomsDocumentTypesRepo(BaseRepository):
    model = CustomsDocumentTypes

    async def get_by_code(self, code: str):
        """Get customs document type by code"""
        query = select(self.model).where(self.model.code == code)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()


class CustomsProceduresRepo(BaseRepository):
    model = CustomsProcedures

    async def get_by_code(self, code: str):
        """Get customs procedure by code"""
        query = select(self.model).where(self.model.code == code)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()


# Junction table repository
class CargoCustomsDocumentsRepo(BaseRepository):
    model = CargoCustomsDocuments

    async def get_by_cargo_id(self, cargo_id: int):
        """Get all customs documents for a specific cargo"""
        query = select(self.model).where(self.model.cargo_id == cargo_id)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_customs_document_id(self, document_id: int):
        """Get all cargo items for a specific customs document"""
        query = select(self.model).where(self.model.customs_document_id == document_id)
        result = await self._session.execute(query)
        return result.scalars().all()


# Complex entity repositories
class CustomsBookingsRepo(BaseRepository):
    model = CustomsBookings

    async def get_bookings_by_vehicle(self, vehicle_id: int):
        """Get all bookings for a specific vehicle"""
        query = select(self.model).where(self.model.vehicle_id == vehicle_id).order_by(self.model.booking_date.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_bookings_by_customs_office(self, office_id: int):
        """Get all bookings for a specific customs office"""
        query = (
            select(self.model)
            .where(self.model.customs_office_id == office_id)
            .order_by(self.model.preferred_entry_timestamp.desc())
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_active_bookings(self):
        """Get all active bookings that require inspection"""
        query = (
            select(self.model)
            .where(self.model.is_inspection_required.is_(True))
            .where(self.model.inspection_id.is_(None))
            .order_by(self.model.preferred_entry_timestamp)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_bookings_by_status(self, status_id: int):
        """Get bookings by status"""
        query = select(self.model).where(self.model.status_id == status_id).order_by(self.model.created_at.desc())
        result = await self._session.execute(query)
        return result.scalars().all()


class CustomsCrossingsRepo(BaseRepository):
    model = CustomsCrossings

    async def get_crossings_by_vehicle(self, vehicle_id: int):
        """Get all border crossings for a specific vehicle"""
        query = select(self.model).where(self.model.vehicle_id == vehicle_id).order_by(self.model.timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_recent_entries(self, limit: int = 50):
        """Get recent entry crossings"""
        query = select(self.model).where(self.model.is_entry.is_(True)).order_by(self.model.entry_timestamp.desc()).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_recent_exits(self, limit: int = 50):
        """Get recent exit crossings"""
        query = select(self.model).where(self.model.is_entry.is_(False)).order_by(self.model.exit_timestamp.desc()).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_crossings_requiring_inspection(self):
        """Get crossings that require inspection but haven't been inspected"""
        query = (
            select(self.model)
            .where(self.model.is_inspection_required.is_(True))
            .where(self.model.is_inspected.is_(False))
            .order_by(self.model.timestamp)
        )
        result = await self._session.execute(query)
        return result.scalars().all()


class CustomsDocumentsRepo(BaseRepository):
    model = CustomsDocuments

    async def get_by_declaration_number(self, declaration_number: str):
        """Get document by declaration number"""
        query = select(self.model).where(self.model.declaration_number == declaration_number)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_documents_by_vehicle(self, vehicle_id: int):
        """Get all customs documents for a specific vehicle"""
        query = select(self.model).where(self.model.vehicle_id == vehicle_id).order_by(self.model.declaration_date.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_pending_inspections(self):
        """Get documents pending inspection"""
        query = select(self.model).where(self.model.is_inspected.is_(False)).order_by(self.model.declaration_date)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_exporter_code(self, exporter_code: str):
        """Get documents by exporter code"""
        query = select(self.model).where(self.model.exporter_code == exporter_code).order_by(self.model.declaration_date.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_importer_code(self, importer_code: str):
        """Get documents by importer code"""
        query = select(self.model).where(self.model.importer_code == importer_code).order_by(self.model.declaration_date.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_transit_documents(self, transit_type_id: int = None):
        """Get transit documents, optionally filtered by type"""
        query = select(self.model)
        if transit_type_id:
            query = query.where(self.model.transit_type_id == transit_type_id)

        query = query.order_by(self.model.entry_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_documents_by_customs_office(self, office_id: int):
        """Get documents processed by specific customs office"""
        query = select(self.model).where(self.model.customs_office_id == office_id).order_by(self.model.declaration_date.desc())
        result = await self._session.execute(query)
        return result.scalars().all()


class CustomsOfficesRepo(BaseRepository):
    model = CustomsOffices

    async def get_by_code(self, code: str):
        """Get customs office by code"""
        query = select(self.model).where(self.model.code == code)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_border_points(self):
        """Get all border point offices"""
        query = select(self.model).where(self.model.is_border_point.is_(True)).order_by(self.model.name_ru)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_region(self, kato_code: str):
        """Get offices by KATO region code"""
        query = select(self.model).where(self.model.kato_code.like(f"{kato_code}%")).order_by(self.model.name_ru)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_active_offices(self):
        """Get all active customs offices"""
        query = (
            select(self.model)
            .join(CustomsOfficeStatuses, self.model.status_id == CustomsOfficeStatuses.id)
            .where(CustomsOfficeStatuses.name_ru == "Активный")  # Assuming 'Активный' status exists
            .order_by(self.model.name_ru)
        )
        result = await self._session.execute(query)
        return result.scalars().all()


class CustomsSealsRepo(BaseRepository):
    model = CustomsSeals

    async def get_by_number(self, number: str):
        """Get seal by number"""
        query = select(self.model).where(self.model.number == number)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_seals_by_vehicle(self, vehicle_id: int):
        """Get active seals for a specific vehicle"""
        query = (
            select(self.model)
            .where(self.model.vehicle_id == vehicle_id)
            .where(self.model.removal_timestamp.is_(None))
            .order_by(self.model.installation_timestamp.desc())
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_seals_by_customs_office(self, office_id: int):
        """Get seals installed by specific customs office"""
        query = (
            select(self.model).where(self.model.customs_office_id == office_id).order_by(self.model.installation_timestamp.desc())
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_removed_seals(self, start_date=None, end_date=None):
        """Get removed seals within date range"""
        query = select(self.model).where(self.model.removal_timestamp.is_not(None))

        if start_date:
            query = query.where(self.model.removal_timestamp >= start_date)
        if end_date:
            query = query.where(self.model.removal_timestamp <= end_date)

        query = query.order_by(self.model.removal_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()


class InspectionsRepo(BaseRepository):
    model = Inspections

    async def get_by_inspector(self, inspector_name: str):
        """Get inspections by inspector name"""
        query = select(self.model).where(self.model.inspector == inspector_name).order_by(self.model.start_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_pending_inspections(self):
        """Get inspections that haven't finished yet"""
        query = select(self.model).where(self.model.end_timestamp.is_(None)).order_by(self.model.start_timestamp)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_completed_inspections(self, start_date=None, end_date=None):
        """Get completed inspections within date range"""
        query = select(self.model).where(self.model.end_timestamp.is_not(None))

        if start_date:
            query = query.where(self.model.end_timestamp >= start_date)
        if end_date:
            query = query.where(self.model.end_timestamp <= end_date)

        query = query.order_by(self.model.end_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_type(self, type_id: int):
        """Get inspections by type"""
        query = select(self.model).where(self.model.type_id == type_id).order_by(self.model.start_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_result(self, result_id: int):
        """Get inspections by result"""
        query = select(self.model).where(self.model.result_id == result_id).order_by(self.model.end_timestamp.desc())
        result = await self._session.execute(query)
        return result.scalars().all()


class SendersRecipientsRepo(BaseRepository):
    model = SendersRecipients

    async def get_by_iin_bin(self, iin_bin: str):
        """Get sender/recipient by IIN/BIN"""
        query = select(self.model).where(self.model.iin_bin == iin_bin)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_organization_id(self, organization_id: int):
        """Get senders/recipients by organization ID"""
        query = select(self.model).where(self.model.organizations_id == organization_id).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_foreign_entities(self):
        """Get all foreign senders/recipients"""
        query = select(self.model).where(self.model.is_foreign.is_(True)).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_domestic_entities(self):
        """Get all domestic senders/recipients"""
        query = select(self.model).where(self.model.is_foreign.is_(False)).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_active_entities(self):
        """Get all active senders/recipients"""
        query = select(self.model).where(self.model.is_active.is_(True)).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_country(self, country_id: int):
        """Get senders/recipients by country"""
        query = select(self.model).where(self.model.country_id == country_id).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def search_by_name(self, name_pattern: str):
        """Search senders/recipients by name pattern"""
        query = select(self.model).where(self.model.name.ilike(f"%{name_pattern}%")).order_by(self.model.name)
        result = await self._session.execute(query)
        return result.scalars().all()

class CustomsCarriersRepo(BaseRepository):
    model = CustomsCarriers

    async def get_base_info(self, customs_id: int): 
        query = select(
            Organizations.name_ru.label('organization_name'),
            CustomsCarriers.iin_bin,
            Organizations.address,
            CustomsCarriers.contact_information,
            Okeds.name_ru.label('oked_name'),
            TaxRegimes.name.label('tax_regime'),
            CustomsCarriers.doc_number,
            CustomsCarriers.date_start,
            CustomsOffices.name_ru.label('customs_office_name'),
            CustomsCarriers.document_number,
            CustomsCarriers.document_date_end,
            CustomsCarriers.other_information
        ).join(
            Organizations,
            CustomsCarriers.organization_id == Organizations.id
        ).join(
            TaxRegimes,
            Organizations.tax_regime_id == TaxRegimes.id
        ).join(
            Okeds,
            Organizations.oked_id == Okeds.id
        ).join(
            CustomsOffices,
            CustomsCarriers.customs_offices_id == CustomsOffices.id
        ).where(CustomsCarriers.id == customs_id)

        result = await self._session.execute(query)
        response = result.mappings().one_or_none()

        return response
        

class RepresentOfficesRepo(BaseRepository):
    model = RepresentOffices

    async def get_base_info(self, office_id: int):
        query = select(
            Organizations.name_ru,
            RepresentOffices.iin_bin,
            Organizations.address,
            Okeds.name_ru,
            TaxRegimes.name,
            RepresentOffices.doc_number,
            RepresentOffices.doc_date
        ).select_from(RepresentOffices).join(
            Organizations,
            RepresentOffices.organization_id == Organizations.id
        ).join(
            TaxRegimes,
            Organizations.tax_regime_id == TaxRegimes.id
        ).join(
            Okeds,
            Organizations.oked_id == Okeds.id
        ).where(RepresentOffices.id == office_id)

        result = await self._session.execute(query)
        response = result.mappings().one_or_none()

        return response