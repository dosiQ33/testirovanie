from sqlalchemy import select, update
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
from loguru import logger
from app.modules.common.repository import BaseRepository
from .dtos import (
    RisksFilterDto,
    RiskUpdateDto,
    RiskBulkUpdateDto,
    OrdersFilterDto,
    OrderPatchDto,
)
from .models import (
    Risks,
    DicRiskDegree,
    DicRiskType,
    DicRiskName,
    DicOrderStatus,
    DicOrderType,
    Orders,
)
from app.modules.ckf.models import Organizations


class DicOrderStatusRepo(BaseRepository):
    model = DicOrderStatus


class DicOrderTypeRepo(BaseRepository):
    model = DicOrderType


class DicRiskDegreeRepo(BaseRepository):
    model = DicRiskDegree


class DicRiskNameRepo(BaseRepository):
    model = DicRiskName


class DicRiskTypeRepo(BaseRepository):
    model = DicRiskType


class RisksRepo(BaseRepository):
    model = Risks

    async def get_risks_with_details(self, filters: RisksFilterDto):
        try:
            query = (
                select(self.model)
                .join(
                    Organizations,
                    self.model.organization_id == Organizations.id,
                    isouter=True,
                )
                .join(DicRiskType, self.model.risk_type == DicRiskType.id, isouter=True)
                .join(DicRiskName, self.model.risk_name == DicRiskName.id, isouter=True)
                .join(
                    DicRiskDegree,
                    self.model.risk_degree == DicRiskDegree.id,
                    isouter=True,
                )
            )

            if filters.risk_degree_id is not None:
                query = query.filter(self.model.risk_degree == filters.risk_degree_id)

            if filters.risk_type_id is not None:
                query = query.filter(self.model.risk_type == filters.risk_type_id)

            if filters.risk_name_id is not None:
                query = query.filter(self.model.risk_name == filters.risk_name_id)

            if filters.iin_bin is not None:
                query = query.filter(Organizations.iin_bin == filters.iin_bin)

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} записей рисков.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске рисков по фильтрам {filters}: {e}")
            raise

    async def update_risk_order(self, risk_id: int, update_data: RiskUpdateDto):
        """Обновление одной записи риска"""
        try:
            update_values = {}
            if update_data.order_id is not None:
                update_values["order_id"] = update_data.order_id
            if update_data.is_ordered is not None:
                update_values["is_ordered"] = update_data.is_ordered

            if not update_values:
                logger.warning(f"Нет данных для обновления риска с ID {risk_id}")
                return 0

            query = (
                update(self.model)
                .where(self.model.id == risk_id)
                .values(**update_values)
            )

            result = await self._session.execute(query)
            updated_count = result.rowcount

            logger.info(f"Обновлено {updated_count} записей риска с ID {risk_id}")
            return updated_count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении риска с ID {risk_id}: {e}")
            raise

    async def bulk_update_risks_order(self, bulk_update: RiskBulkUpdateDto):
        """Массовое обновление рисков"""
        try:
            update_values = {}
            if bulk_update.order_id is not None:
                update_values["order_id"] = bulk_update.order_id
            if bulk_update.is_ordered is not None:
                update_values["is_ordered"] = bulk_update.is_ordered

            if not update_values:
                logger.warning("Нет данных для массового обновления рисков")
                return 0

            query = (
                update(self.model)
                .where(self.model.id.in_(bulk_update.risk_ids))
                .values(**update_values)
            )

            result = await self._session.execute(query)
            updated_count = result.rowcount

            logger.info(f"Массово обновлено {updated_count} записей рисков")
            return updated_count

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении рисков: {e}")
            raise

    async def get_risk_by_id(self, risk_id: int):
        """Получение риска по ID для проверки существования"""
        try:
            query = select(self.model).where(self.model.id == risk_id)
            result = await self._session.execute(query)
            record = result.unique().scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске риска с ID {risk_id}: {e}")
            raise


class OrdersRepo(BaseRepository):
    model = Orders

    async def filter_orders(self, filters: OrdersFilterDto):
        """Получить поручения с фильтрацией"""
        try:
            query = select(self.model)

            if filters.order_date_from is not None:
                query = query.filter(self.model.order_date >= filters.order_date_from)

            if filters.order_date_to is not None:
                query = query.filter(self.model.order_date <= filters.order_date_to)

            if filters.order_deadline_from is not None:
                query = query.filter(
                    self.model.order_deadline >= filters.order_deadline_from
                )

            if filters.order_deadline_to is not None:
                query = query.filter(
                    self.model.order_deadline <= filters.order_deadline_to
                )

            if filters.order_num is not None:
                query = query.filter(self.model.order_num == filters.order_num)

            if filters.employee_id is not None:
                query = query.filter(self.model.employee_id == filters.employee_id)

            if filters.order_status is not None:
                query = query.filter(self.model.order_status == filters.order_status)

            if filters.order_type is not None:
                query = query.filter(self.model.order_type == filters.order_type)

            query = query.order_by(self.model.order_date.desc())

            result = await self._session.execute(query)
            records = result.unique().scalars().all()

            logger.info(f"Найдено {len(records)} поручений.")
            return records

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске поручений по фильтрам {filters}: {e}")
            raise

    async def patch_order(self, order_id: int, order_data: OrderPatchDto) -> Orders:
        """Частично обновить поручение (только переданные поля)"""
        try:
            logger.info(
                f"Частичное обновление поручения ID={order_id} с параметрами: {order_data.model_dump(exclude_unset=True)}"
            )

            existing_order = await self.get_one_by_id(order_id)
            if not existing_order:
                raise HTTPException(
                    status_code=404, detail=f"Поручение с ID {order_id} не найдено"
                )

            update_data = order_data.model_dump(exclude_unset=True, exclude_none=True)

            if not update_data:
                raise HTTPException(
                    status_code=400, detail="Не передано ни одного поля для обновления"
                )

            for field, value in update_data.items():
                if hasattr(existing_order, field):
                    setattr(existing_order, field, value)

            await self._session.flush()
            await self._session.refresh(existing_order)

            logger.info(
                f"Поручение ID={order_id} успешно обновлено. Обновленные поля: {list(update_data.keys())}"
            )
            return existing_order

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при частичном обновлении поручения ID={order_id}: {e}"
            )
            raise HTTPException(
                status_code=500, detail=f"Ошибка при обновлении поручения: {str(e)}"
            )
