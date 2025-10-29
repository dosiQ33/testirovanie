from sqlalchemy import select

from app.modules.common.repository import BaseRepository

from .models import (
    Cargos
)

from ..customs.models import (
    CustomsDocuments
)

from ..common.models import (
    TnVed
)

class CargosRepository(BaseRepository):
    model = Cargos

    async def get_cargo_info(self, document_id: int):
        query = (
            select(
                CustomsDocuments.declaration_number,
                CustomsDocuments.declaration_date,
                CustomsDocuments.departure_country_id,
                CustomsDocuments.destination_country_id,
                # TnVed.code,  откоментить когда заполнят tnved
                # Cargos.count  откоментить когда заполнят cargos
            )
            # .select_from(Cargos) откоментить когда заполнят cargos
            # .join(TnVed, Cargos.tn_ved_id == TnVed.id) откоментить когда заполнят cargos
            # .join(CustomsDocuments, Cargos.customs_document_id == CustomsDocuments.id) откоментить когда заполнят cargos
            .where(CustomsDocuments.id == document_id)
        )

        result = await self._session.execute(query)
        response = result.all()



        return [res._mapping for res in response]