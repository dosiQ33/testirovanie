from sqlalchemy import (
    select,
    union_all
)
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.modules.common.repository import (
    BaseRepository,
)

from .models import (
    Lands,
    Subjects,
    Document,
    LandRights,
    LandIdentityDocs,
    Infrastructures,
    LandEconomicChars,
    LandRestriction,
    RefRestriciton,
    RefChargeTypes,
    LandCharges,
    LandChargeDocs,
    RefLandCategory
)

class LandsRepository(BaseRepository):
    model = Lands

    async def get_legal_information(self, land_id: int):
        try:
            query = (
                select(
                    Subjects.iin,
                    Subjects.bin,
                    Subjects.first_name,
                    Subjects.last_name,
                    Document.name_ru.label('document_name_ru'),
                    LandRights.start_date
                )
                .join(
                    LandRights,
                    Subjects.id == LandRights.owner_subject_id
                )
                .join(
                    Lands,
                    LandRights.land_id == Lands.id
                )
                .join(
                    LandIdentityDocs,
                    Lands.id == LandIdentityDocs.land_id
                )
                .join(
                    Document,
                    LandIdentityDocs.document_id == Document.id
                )
                .where(
                    Lands.id == land_id
                )
            )
            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных по ЗУ {land_id}: {e}")
            raise

    async def get_land_infrastructure(self, land_id: int):
        try:
            query = (
                select(
                    Infrastructures.electricity,
                    Infrastructures.water,
                    Infrastructures.gas,
                    Infrastructures.sewage,
                    Infrastructures.internet,
                    Infrastructures.road_type,
                    Infrastructures.distance_to_city_km
                )
                .where(
                    Infrastructures.land_id == land_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных по ЗУ {land_id}: {e}")
            raise    
    
    async def get_ecological_info(self, land_id: int):
        try:
            query= (
                select(
                    RefLandCategory.name_ru.label("land_type"),
                    RefRestriciton.name_ru.label("restriction")
                )
                .select_from(Lands)
                .join(
                    RefLandCategory,
                    RefLandCategory.id == Lands.land_category_id
                )
                .join(
                    LandRestriction, 
                    LandRestriction.land_id == Lands.id
                )
                .join(
                    RefRestriciton,
                    RefRestriciton.id == LandRestriction.type_id
                )
                .where(Lands.id == land_id)
            )

            result = await self._session.execute(query)
            row = result.one()

            if row:
                land_type, restriction = row
                return {"land_type": land_type, "restriction": restriction}
            else:
                return None
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных по ЗУ {land_id}: {e}")
            raise

    async def get_land_restrictions(self, land_id: int):
        try:
            query = (
                select(
                    RefChargeTypes.name_ru,
                    LandCharges.start_date,
                    LandCharges.validity_ru,
                    LandChargeDocs.reason_type,
                    LandCharges.start_date,
                    LandCharges.validity_ru,
                    LandRestriction.name_ru,
                    LandRestriction.start_date,
                    LandRestriction.validity_ru,
                    LandRestriction.imposed_subject_id
                )
                .join(
                    Lands,
                    LandCharges.land_id == Lands.id
                )
                .join(
                    LandRestriction,
                    Lands.id == LandRestriction.land_id
                )
                .join(
                    RefRestriciton,
                    LandRestriction.type_id == RefRestriciton.id
                )
                .where(
                    Lands.id == land_id
                )
            )

            result = await self._session.execute(query)
            response = result.mappings().one()

            return response
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении данных по ЗУ {land_id}: {e}")
            raise    