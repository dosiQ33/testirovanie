from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends
from datetime import datetime
from clickhouse_connect.driver import Client
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache
from loguru import logger

from app.database.deps import get_session_with_commit
from app.modules.common.router import request_key_builder, cache_ttl
from app.modules.ckf.repository import (
    OrganizationsRepo,
)
from app.modules.ckf.dtos import OrganizationDto
from .deps import get_clickhouse_client
from .dtos import (
    KkmsClickDto,
    ReceiptsClickDto,
    ReceiptsWithKkmDto,
    ReceiptsStatsDto,
    GetReceiptByFiscalKkmRegNumberClickDto,
    GetReceiptByFiscalKkmSerialNumberClickDto,
    GetReceiptByFiscalOrganizationClickDto,
)
from .repository import KkmsClickRepository, ReceiptsClickRepository


router = APIRouter(prefix="/receipts-click")


class KkmsClickRouter(APIRouter):
    """Роутер для работы с ККМ из ClickHouse"""

    sub_router = APIRouter(prefix="/kkms", tags=["clickhouse: kkms"])

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    @sub_router.get("/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_by_id(
        kkm_id: int,
        client: Client = Depends(get_clickhouse_client),
    ) -> KkmsClickDto:
        """Получить ККМ по ID"""
        repo = KkmsClickRepository(client)
        kkm = await repo.get_by_id(kkm_id)

        if not kkm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ККМ с ID {kkm_id} не найдена",
            )

        return kkm

    @sub_router.get("/organization/{organization_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkms_by_organization_id(
        organization_id: int,
        client: Client = Depends(get_clickhouse_client),
    ) -> List[KkmsClickDto]:
        """Получить все ККМ организации"""
        repo = KkmsClickRepository(client)
        kkms = await repo.get_by_organization_id(organization_id)

        if not kkms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ККМ для организации с ID {organization_id} не найдены",
            )

        return kkms

    @sub_router.get("/reg-number/{reg_number}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_by_reg_number(
        reg_number: str,
        client: Client = Depends(get_clickhouse_client),
    ) -> KkmsClickDto:
        """Получить ККМ по регистрационному номеру"""
        repo = KkmsClickRepository(client)
        kkm = await repo.get_by_reg_number(reg_number)

        if not kkm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ККМ с регистрационным номером {reg_number} не найдена",
            )

        return kkm

    @sub_router.get("/serial-number/{serial_number}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_kkm_by_serial_number(
        serial_number: str,
        client: Client = Depends(get_clickhouse_client),
    ) -> KkmsClickDto:
        """Получить ККМ по серийному номеру"""
        repo = KkmsClickRepository(client)
        kkm = await repo.get_by_serial_number(serial_number)

        if not kkm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ККМ с серийным номером {serial_number} не найдена",
            )

        return kkm


class ReceiptsClickRouter(APIRouter):
    """Роутер для работы с чеками из ClickHouse (аналог RiskInfosRouter)"""

    sub_router = APIRouter(prefix="/receipts", tags=["clickhouse: receipts"])

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    @sub_router.get("/kkm/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_by_kkm_id(
        kkm_id: int,
        limit: int = Query(default=100, description="Максимальное количество записей"),
        client: Client = Depends(get_clickhouse_client),
    ) -> List[ReceiptsClickDto]:
        """
        Получить чеки по ID ККМ (аналог get_by_organization_id из RiskInfosRouter)

        - **kkm_id**: ID ККМ
        - **limit**: максимальное количество записей (по умолчанию 100)
        """
        repo = ReceiptsClickRepository(client)
        receipts = await repo.get_by_kkm_id(kkm_id, limit)

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки для ККМ с ID {kkm_id} не найдены",
            )

        logger.info(f"Найдено {len(receipts)} чеков для ККМ {kkm_id}")
        return receipts

    @sub_router.get("/organization/{organization_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_by_organization_id(
        organization_id: int,
        limit: int = Query(default=100, description="Максимальное количество записей"),
        include_organization_details: bool = Query(
            default=False, description="Включить детальную информацию об организации"
        ),
        client: Client = Depends(get_clickhouse_client),
        pg_session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по ID организации с информацией о ККМ

        - **organization_id**: ID организации
        - **limit**: максимальное количество записей (по умолчанию 100)
        - **include_organization_details**: получить детальную информацию об организации из PostgreSQL
        """
        repo = ReceiptsClickRepository(client)
        receipts = await repo.get_by_organization_id(organization_id, limit)

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки для организации с ID {organization_id} не найдены",
            )

        organization_data = None
        if include_organization_details:
            try:
                org_repo = OrganizationsRepo(pg_session)
                organization = await org_repo.get_one_by_id(organization_id)
                if organization:
                    organization_data = OrganizationDto.model_validate(organization)
                else:
                    logger.warning(
                        f"Организация с ID {organization_id} не найдена в PostgreSQL"
                    )
            except Exception as e:
                logger.error(f"Ошибка при получении организации из PostgreSQL: {e}")

        result = []
        for receipt in receipts:
            receipt_dict = receipt.model_dump()
            if organization_data:
                receipt_dict["organization"] = organization_data
            result.append(ReceiptsWithKkmDto(**receipt_dict))

        logger.info(f"Найдено {len(receipts)} чеков для организации {organization_id}")
        return result

    @sub_router.get("/fiscal-kkm-reg-number")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_by_fiscal_and_kkm_reg_number(
        dto: Annotated[GetReceiptByFiscalKkmRegNumberClickDto, Query()],
        client: Client = Depends(get_clickhouse_client),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по фискальному признаку и регистрационному номеру ККМ

        - **fiskal_sign**: фискальный признак
        - **kkm_reg_number**: регистрационный номер ККМ
        """
        repo = ReceiptsClickRepository(client)
        receipts = await repo.get_by_fiscal_and_kkm_reg_number(
            fiskal_sign=dto.fiskal_sign, kkm_reg_number=dto.kkm_reg_number
        )

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки по фискальному признаку {dto.fiskal_sign} и регистрационному номеру ККМ {dto.kkm_reg_number} не найдены",
            )

        logger.info(
            f"Найдено {len(receipts)} чеков по фискальному признаку {dto.fiskal_sign} и рег. номеру {dto.kkm_reg_number}"
        )
        return receipts

    @sub_router.get("/fiscal-kkm-serial-number")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_by_fiscal_and_kkm_serial_number(
        dto: Annotated[GetReceiptByFiscalKkmSerialNumberClickDto, Query()],
        client: Client = Depends(get_clickhouse_client),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по фискальному признаку и серийному номеру ККМ

        - **fiskal_sign**: фискальный признак
        - **kkm_serial_number**: серийный номер ККМ
        """
        repo = ReceiptsClickRepository(client)
        receipts = await repo.get_by_fiscal_and_kkm_serial_number(
            fiskal_sign=dto.fiskal_sign, kkm_serial_number=dto.kkm_serial_number
        )

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки по фискальному признаку {dto.fiskal_sign} и серийному номеру ККМ {dto.kkm_serial_number} не найдены",
            )

        logger.info(
            f"Найдено {len(receipts)} чеков по фискальному признаку {dto.fiskal_sign} и серийному номеру {dto.kkm_serial_number}"
        )
        return receipts

    @sub_router.get("/fiscal-organization")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_by_fiscal_and_organization_id(
        dto: Annotated[GetReceiptByFiscalOrganizationClickDto, Query()],
        include_organization_details: bool = Query(
            default=False, description="Включить детальную информацию об организации"
        ),
        client: Client = Depends(get_clickhouse_client),
        pg_session: AsyncSession = Depends(get_session_with_commit),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по фискальному признаку и ID организации

        - **fiskal_sign**: фискальный признак
        - **organization_id**: ID организации
        - **include_organization_details**: получить детальную информацию об организации из PostgreSQL(with id)
        """
        kkms_repo = KkmsClickRepository(client)
        kkms = await kkms_repo.get_by_organization_id(dto.organization_id)

        if not kkms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ККМ для организации с ID {dto.organization_id} не найдены",
            )

        receipts_repo = ReceiptsClickRepository(client)
        all_receipts = []

        for kkm in kkms:
            try:
                if kkm.reg_number:
                    receipts = await receipts_repo.get_by_fiscal_and_kkm_reg_number(
                        fiskal_sign=dto.fiskal_sign, kkm_reg_number=kkm.reg_number
                    )
                    all_receipts.extend(receipts)

                if not all_receipts and kkm.serial_number:
                    receipts = await receipts_repo.get_by_fiscal_and_kkm_serial_number(
                        fiskal_sign=dto.fiskal_sign, kkm_serial_number=kkm.serial_number
                    )
                    all_receipts.extend(receipts)

            except Exception as e:
                logger.warning(f"Ошибка при поиске чеков для ККМ {kkm.id}: {e}")
                continue

        if not all_receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки по фискальному признаку {dto.fiskal_sign} и организации {dto.organization_id} не найдены",
            )

        organization_data = None
        if include_organization_details:
            try:
                org_repo = OrganizationsRepo(pg_session)
                organization = await org_repo.get_one_by_id(dto.organization_id)
                if organization:
                    organization_data = OrganizationDto.model_validate(organization)
            except Exception as e:
                logger.error(f"Ошибка при получении организации из PostgreSQL: {e}")

        result = []
        for receipt in all_receipts:
            receipt_dict = receipt.model_dump()
            if organization_data:
                receipt_dict["organization"] = organization_data
            result.append(ReceiptsWithKkmDto(**receipt_dict))

        logger.info(
            f"Найдено {len(all_receipts)} чеков по фискальному признаку {dto.fiskal_sign} и организации {dto.organization_id}"
        )
        return result

    @sub_router.get("/stats/kkm/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_receipts_stats_by_kkm_id(
        kkm_id: int,
        date_from: Optional[datetime] = Query(None, description="Дата начала периода"),
        date_to: Optional[datetime] = Query(None, description="Дата окончания периода"),
        client: Client = Depends(get_clickhouse_client),
    ) -> ReceiptsStatsDto:
        """
        Получить статистику по чекам для ККМ

        - **kkm_id**: ID ККМ
        - **date_from**: дата начала периода (опционально)
        - **date_to**: дата окончания периода (опционально)
        """
        repo = ReceiptsClickRepository(client)
        stats = await repo.get_stats_by_kkm_id(kkm_id, date_from, date_to)

        logger.info(
            f"Получена статистика для ККМ {kkm_id}: {stats.total_receipts} чеков, общая сумма {stats.total_amount}"
        )
        return stats


router.include_router(KkmsClickRouter())
router.include_router(ReceiptsClickRouter())
