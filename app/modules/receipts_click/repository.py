from typing import List, Optional, Dict, Any
from clickhouse_connect.driver import Client
from loguru import logger
from datetime import datetime

from .dtos import (
    KkmsClickDto,
    ReceiptsClickDto,
    ReceiptsWithKkmDto,
    ReceiptsFilterDto,
    ReceiptsStatsDto,
    StatDayDto,
    StatYearDto,
    KkmStatsDto,
)


class BaseClickRepository:
    """Базовый репозиторий для работы с ClickHouse"""

    def __init__(self, client: Client):
        self.client = client

    def _row_to_dict(self, row: tuple, columns: List[str]) -> Dict[str, Any]:
        """Преобразование строки результата в словарь"""
        return dict(zip(columns, row))

    def _rows_to_dicts(
        self, rows: List[tuple], columns: List[str]
    ) -> List[Dict[str, Any]]:
        """Преобразование строк результата в список словарей"""
        return [self._row_to_dict(row, columns) for row in rows]


class KkmsClickRepository(BaseClickRepository):
    """Репозиторий для работы с ККМ в ClickHouse"""

    table_name = "kkms"

    async def get_by_id(self, kkm_id: int) -> Optional[KkmsClickDto]:
        """Получить ККМ по ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %(kkm_id)s LIMIT 1"
            result = self.client.query(query, parameters={"kkm_id": kkm_id})

            if not result.result_rows:
                return None

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)
            return KkmsClickDto(**row_dict)

        except Exception as e:
            logger.error(f"Ошибка при получении ККМ по ID {kkm_id}: {e}")
            raise

    async def get_by_organization_id(self, organization_id: int) -> List[KkmsClickDto]:
        """Получить ККМ по ID организации"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE organization_id = %(organization_id)s"
            result = self.client.query(
                query, parameters={"organization_id": organization_id}
            )

            rows_dicts = self._rows_to_dicts(result.result_rows, result.column_names)
            return [KkmsClickDto(**row) for row in rows_dicts]

        except Exception as e:
            logger.error(
                f"Ошибка при получении ККМ по organization_id {organization_id}: {e}"
            )
            raise

    async def get_by_reg_number(self, reg_number: str) -> Optional[KkmsClickDto]:
        """Получить ККМ по регистрационному номеру"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE reg_number = %(reg_number)s LIMIT 1"
            result = self.client.query(query, parameters={"reg_number": reg_number})

            if not result.result_rows:
                return None

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)
            return KkmsClickDto(**row_dict)

        except Exception as e:
            logger.error(f"Ошибка при получении ККМ по reg_number {reg_number}: {e}")
            raise

    async def get_by_serial_number(self, serial_number: str) -> Optional[KkmsClickDto]:
        """Получить ККМ по серийному номеру"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE serial_number = %(serial_number)s LIMIT 1"
            result = self.client.query(
                query, parameters={"serial_number": serial_number}
            )

            if not result.result_rows:
                return None

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)
            return KkmsClickDto(**row_dict)

        except Exception as e:
            logger.error(
                f"Ошибка при получении ККМ по serial_number {serial_number}: {e}"
            )
            raise


class ReceiptsClickRepository(BaseClickRepository):
    """Репозиторий для работы с чеками в ClickHouse"""

    table_name = "testr"
    kkms_table_name = "kkms"

    async def get_by_kkm_id(
        self, kkm_id: int, limit: int = 100
    ) -> List[ReceiptsClickDto]:
        """Получить чеки по ID ККМ"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE kkms_id = %(kkm_id)s 
                ORDER BY operation_date DESC 
                LIMIT %(limit)s
            """
            result = self.client.query(
                query, parameters={"kkm_id": kkm_id, "limit": limit}
            )

            rows_dicts = self._rows_to_dicts(result.result_rows, result.column_names)
            return [ReceiptsClickDto(**row) for row in rows_dicts]

        except Exception as e:
            logger.error(f"Ошибка при получении чеков по kkm_id {kkm_id}: {e}")
            raise

    async def get_by_organization_id(
        self, organization_id: int, limit: int = 100
    ) -> List[ReceiptsWithKkmDto]:
        """Получить чеки по ID организации с информацией о ККМ"""
        try:
            query = f"""
                SELECT 
                    r.*,
                    k.id as kkm_id,
                    k.organization_id as kkm_organization_id,
                    k.reg_number as kkm_reg_number,
                    k.serial_number as kkm_serial_number,
                    k.model_name as kkm_model_name,
                    k.made_year as kkm_made_year,
                    k.date_start as kkm_date_start,
                    k.date_stop as kkm_date_stop,
                    k.address as kkm_address,
                    k.shape as kkm_shape,
                    k.created_at as kkm_created_at,
                    k.updated_at as kkm_updated_at
                FROM {self.table_name} r
                LEFT JOIN {self.kkms_table_name} k ON r.kkms_id = k.id
                WHERE k.organization_id = %(organization_id)s
                ORDER BY r.operation_date DESC
                LIMIT %(limit)s
            """
            result = self.client.query(
                query, parameters={"organization_id": organization_id, "limit": limit}
            )

            receipts_with_kkm = []
            for row in result.result_rows:
                row_dict = self._row_to_dict(row, result.column_names)

                receipt_data = {
                    k: v for k, v in row_dict.items() if not k.startswith("kkm_")
                }

                kkm_data = {}
                for k, v in row_dict.items():
                    if k.startswith("kkm_"):
                        kkm_key = k[4:]
                        if kkm_key == "id":
                            kkm_data["id"] = v
                        elif kkm_key == "organization_id":
                            kkm_data["organization_id"] = v
                        else:
                            kkm_data[kkm_key] = v

                kkm = KkmsClickDto(**kkm_data) if kkm_data.get("id") else None

                receipts_with_kkm.append(ReceiptsWithKkmDto(**receipt_data, kkm=kkm))

            return receipts_with_kkm

        except Exception as e:
            logger.error(
                f"Ошибка при получении чеков по organization_id {organization_id}: {e}"
            )
            raise

    async def get_by_fiscal_and_kkm_reg_number(
        self, fiskal_sign: str, kkm_reg_number: str
    ) -> List[ReceiptsWithKkmDto]:
        """Получить чеки по фискальному признаку и регистрационному номеру ККМ"""
        try:
            query = f"""
                SELECT 
                    r.*,
                    k.id as kkm_id,
                    k.organization_id as kkm_organization_id,
                    k.reg_number as kkm_reg_number,
                    k.serial_number as kkm_serial_number,
                    k.model_name as kkm_model_name,
                    k.made_year as kkm_made_year,
                    k.date_start as kkm_date_start,
                    k.date_stop as kkm_date_stop,
                    k.address as kkm_address,
                    k.shape as kkm_shape,
                    k.created_at as kkm_created_at,
                    k.updated_at as kkm_updated_at
                FROM {self.table_name} r
                LEFT JOIN {self.kkms_table_name} k ON r.kkms_id = k.id
                WHERE r.fiskal_sign = %(fiskal_sign)s AND k.reg_number = %(kkm_reg_number)s
                ORDER BY r.operation_date DESC
            """
            result = self.client.query(
                query,
                parameters={
                    "fiskal_sign": fiskal_sign,
                    "kkm_reg_number": kkm_reg_number,
                },
            )

            receipts_with_kkm = []
            for row in result.result_rows:
                row_dict = self._row_to_dict(row, result.column_names)

                receipt_data = {
                    k: v for k, v in row_dict.items() if not k.startswith("kkm_")
                }

                kkm_data = {}
                for k, v in row_dict.items():
                    if k.startswith("kkm_"):
                        kkm_key = k[4:]
                        if kkm_key == "id":
                            kkm_data["id"] = v
                        elif kkm_key == "organization_id":
                            kkm_data["organization_id"] = v
                        else:
                            kkm_data[kkm_key] = v

                kkm = KkmsClickDto(**kkm_data) if kkm_data.get("id") else None

                receipts_with_kkm.append(ReceiptsWithKkmDto(**receipt_data, kkm=kkm))

            return receipts_with_kkm

        except Exception as e:
            logger.error(
                f"Ошибка при получении чеков по fiskal_sign {fiskal_sign} и kkm_reg_number {kkm_reg_number}: {e}"
            )
            raise

    async def get_by_fiscal_and_kkm_serial_number(
        self, fiskal_sign: str, kkm_serial_number: str
    ) -> List[ReceiptsWithKkmDto]:
        """Получить чеки по фискальному признаку и серийному номеру ККМ"""
        try:
            query = f"""
                SELECT 
                    r.*,
                    k.id as kkm_id,
                    k.organization_id as kkm_organization_id,
                    k.reg_number as kkm_reg_number,
                    k.serial_number as kkm_serial_number,
                    k.model_name as kkm_model_name,
                    k.made_year as kkm_made_year,
                    k.date_start as kkm_date_start,
                    k.date_stop as kkm_date_stop,
                    k.address as kkm_address,
                    k.shape as kkm_shape,
                    k.created_at as kkm_created_at,
                    k.updated_at as kkm_updated_at
                FROM {self.table_name} r
                LEFT JOIN {self.kkms_table_name} k ON r.kkms_id = k.id
                WHERE r.fiskal_sign = %(fiskal_sign)s AND k.serial_number = %(kkm_serial_number)s
                ORDER BY r.operation_date DESC
            """
            result = self.client.query(
                query,
                parameters={
                    "fiskal_sign": fiskal_sign,
                    "kkm_serial_number": kkm_serial_number,
                },
            )

            receipts_with_kkm = []
            for row in result.result_rows:
                row_dict = self._row_to_dict(row, result.column_names)

                receipt_data = {
                    k: v for k, v in row_dict.items() if not k.startswith("kkm_")
                }

                kkm_data = {}
                for k, v in row_dict.items():
                    if k.startswith("kkm_"):
                        kkm_key = k[4:]
                        if kkm_key == "id":
                            kkm_data["id"] = v
                        elif kkm_key == "organization_id":
                            kkm_data["organization_id"] = v
                        else:
                            kkm_data[kkm_key] = v

                kkm = KkmsClickDto(**kkm_data) if kkm_data.get("id") else None

                receipts_with_kkm.append(ReceiptsWithKkmDto(**receipt_data, kkm=kkm))

            return receipts_with_kkm

        except Exception as e:
            logger.error(
                f"Ошибка при получении чеков по fiskal_sign {fiskal_sign} и kkm_serial_number {kkm_serial_number}: {e}"
            )
            raise

    async def get_stats_by_kkm_id(
        self,
        kkm_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> ReceiptsStatsDto:
        """Получить статистику по чекам для ККМ"""
        try:
            where_conditions = ["kkms_id = %(kkm_id)s"]
            parameters = {"kkm_id": kkm_id}

            if date_from:
                where_conditions.append("operation_date >= %(date_from)s")
                parameters["date_from"] = date_from

            if date_to:
                where_conditions.append("operation_date <= %(date_to)s")
                parameters["date_to"] = date_to

            where_clause = " AND ".join(where_conditions)

            query = f"""
                SELECT 
                    count(*) as total_receipts,
                    sum(full_item_price) as total_amount,
                    avg(full_item_price) as avg_amount,
                    min(full_item_price) as min_amount,
                    max(full_item_price) as max_amount
                FROM {self.table_name}
                WHERE {where_clause}
            """

            result = self.client.query(query, parameters=parameters)

            if not result.result_rows:
                return ReceiptsStatsDto(
                    total_receipts=0,
                    total_amount=0.0,
                    avg_amount=0.0,
                    min_amount=0.0,
                    max_amount=0.0,
                    period_start=date_from,
                    period_end=date_to,
                )

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)

            return ReceiptsStatsDto(
                total_receipts=row_dict["total_receipts"] or 0,
                total_amount=row_dict["total_amount"] or 0.0,
                avg_amount=row_dict["avg_amount"] or 0.0,
                min_amount=row_dict["min_amount"] or 0.0,
                max_amount=row_dict["max_amount"] or 0.0,
                period_start=date_from,
                period_end=date_to,
            )

        except Exception as e:
            logger.error(f"Ошибка при получении статистики по kkm_id {kkm_id}: {e}")
            raise


class StatsClickRepository(BaseClickRepository):
    """Репозиторий для работы со статистикой в ClickHouse - ТОЛЬКО таблицы stat_day и stat_year"""

    async def get_day_stats_by_kkm_id(self, kkm_id: int) -> Optional[StatDayDto]:
        """Получить статистику за день для ККМ из таблицы stat_day"""
        try:
            query = "SELECT kkms_id, check_sum, check_count FROM stat_day WHERE kkms_id = %(kkm_id)s LIMIT 1"
            result = self.client.query(query, parameters={"kkm_id": kkm_id})

            if not result.result_rows:
                logger.info(f"Статистика за день для ККМ {kkm_id} не найдена")
                return None

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)
            return StatDayDto(**row_dict)

        except Exception as e:
            logger.error(
                f"Ошибка при получении статистики за день для ККМ {kkm_id}: {e}"
            )
            raise

    async def get_year_stats_by_kkm_id(self, kkm_id: int) -> Optional[StatYearDto]:
        """Получить статистику за год для ККМ из таблицы stat_year"""
        try:
            query = "SELECT kkms_id, check_sum, check_count FROM stat_year WHERE kkms_id = %(kkm_id)s LIMIT 1"
            result = self.client.query(query, parameters={"kkm_id": kkm_id})

            if not result.result_rows:
                logger.info(f"Статистика за год для ККМ {kkm_id} не найдена")
                return None

            row_dict = self._row_to_dict(result.result_rows[0], result.column_names)
            return StatYearDto(**row_dict)

        except Exception as e:
            logger.error(
                f"Ошибка при получении статистики за год для ККМ {kkm_id}: {e}"
            )
            raise

    async def get_combined_stats_by_kkm_id(self, kkm_id: int) -> KkmStatsDto:
        """Получить объединенную статистику (день + год) для ККМ"""
        try:
            # Получаем статистику за день и за год
            day_stats = await self.get_day_stats_by_kkm_id(kkm_id)
            year_stats = await self.get_year_stats_by_kkm_id(kkm_id)

            return KkmStatsDto(
                kkms_id=kkm_id, day_stats=day_stats, year_stats=year_stats
            )

        except Exception as e:
            logger.error(
                f"Ошибка при получении объединенной статистики для ККМ {kkm_id}: {e}"
            )
            raise
