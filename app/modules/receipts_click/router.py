from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends
from datetime import datetime
from clickhouse_connect.driver import Client
from fastapi_cache.decorator import cache
from loguru import logger

from app.modules.common.router import request_key_builder, cache_ttl
from .deps import get_clickhouse_client
from .dtos import (
    KkmsClickDto,
    ReceiptsClickDto,
    ReceiptsWithKkmDto,
    ReceiptsStatsDto,
    GetReceiptByFiscalKkmRegNumberClickDto,
    GetReceiptByFiscalKkmSerialNumberClickDto,
    GetReceiptByFiscalOrganizationClickDto,
    StatDayDto,
    StatYearDto,
    KkmStatsDto,
)
from .repository import (
    KkmsClickRepository,
    ReceiptsClickRepository,
    StatsClickRepository,
)


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
    """Роутер для работы с чеками из ClickHouse"""

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
        Получить чеки по ID ККМ

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
        client: Client = Depends(get_clickhouse_client),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по ID организации с информацией о ККМ

        - **organization_id**: ID организации
        - **limit**: максимальное количество записей (по умолчанию 100)
        """
        repo = ReceiptsClickRepository(client)
        receipts = await repo.get_by_organization_id(organization_id, limit)

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чеки для организации с ID {organization_id} не найдены",
            )

        logger.info(f"Найдено {len(receipts)} чеков для организации {organization_id}")
        return receipts

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
        client: Client = Depends(get_clickhouse_client),
    ) -> List[ReceiptsWithKkmDto]:
        """
        Получить чеки по фискальному признаку и ID организации

        - **fiskal_sign**: фискальный признак
        - **organization_id**: ID организации
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

        logger.info(
            f"Найдено {len(all_receipts)} чеков по фискальному признаку {dto.fiskal_sign} и организации {dto.organization_id}"
        )
        return all_receipts

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


class StatsClickRouter(APIRouter):
    """Роутер для работы со статистикой из ClickHouse - ТОЛЬКО таблицы stat_day и stat_year"""

    sub_router = APIRouter(prefix="/stats", tags=["clickhouse: stats"])

    def __init__(self):
        super().__init__()
        self.include_router(self.sub_router)

    @sub_router.get("/day/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_day_stats_by_kkm_id(
        kkm_id: int,
        client: Client = Depends(get_clickhouse_client),
    ) -> StatDayDto:
        """
        Получить статистику за день для ККМ из таблицы stat_day

        - **kkm_id**: ID ККМ

        Возвращает:
        - kkms_id: ID ККМ
        - check_sum: сумма чеков за день
        - check_count: количество чеков за день
        """
        repo = StatsClickRepository(client)
        stats = await repo.get_day_stats_by_kkm_id(kkm_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статистика за день для ККМ с ID {kkm_id} не найдена",
            )

        logger.info(
            f"Получена статистика за день для ККМ {kkm_id}: сумма={stats.check_sum}, количество={stats.check_count}"
        )
        return stats

    @sub_router.get("/year/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_year_stats_by_kkm_id(
        kkm_id: int,
        client: Client = Depends(get_clickhouse_client),
    ) -> StatYearDto:
        """
        Получить статистику за год для ККМ из таблицы stat_year

        - **kkm_id**: ID ККМ

        Возвращает:
        - kkms_id: ID ККМ
        - check_sum: сумма чеков за год
        - check_count: количество чеков за год
        """
        repo = StatsClickRepository(client)
        stats = await repo.get_year_stats_by_kkm_id(kkm_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статистика за год для ККМ с ID {kkm_id} не найдена",
            )

        logger.info(
            f"Получена статистика за год для ККМ {kkm_id}: сумма={stats.check_sum}, количество={stats.check_count}"
        )
        return stats

    @sub_router.get("/combined/{kkm_id}")
    @cache(expire=cache_ttl, key_builder=request_key_builder)
    async def get_combined_stats_by_kkm_id(
        kkm_id: int,
        client: Client = Depends(get_clickhouse_client),
    ) -> KkmStatsDto:
        """
        Получить объединенную статистику (день + год) для ККМ

        - **kkm_id**: ID ККМ

        Возвращает:
        - kkms_id: ID ККМ
        - day_stats: статистика за день (сумма и количество)
        - year_stats: статистика за год (сумма и количество)
        """
        stats_repo = StatsClickRepository(client)
        combined_stats = await stats_repo.get_combined_stats_by_kkm_id(kkm_id)

        # Если нет ни дневной, ни годовой статистики, возвращаем 404
        if not combined_stats.day_stats and not combined_stats.year_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статистика для ККМ с ID {kkm_id} не найдена",
            )

        logger.info(f"Получена объединенная статистика для ККМ {kkm_id}")
        return combined_stats


router.include_router(KkmsClickRouter())
router.include_router(ReceiptsClickRouter())
router.include_router(StatsClickRouter())
