from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import ForeignKey, BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.modules.common.models import BasestModel

if TYPE_CHECKING:
    from app.modules.admins.models import Employees


class DicOrderStatus(BasestModel):
    __tablename__ = "dic_order_status"
    __table_args__ = dict(schema="orders", comment="Статусы поручнии")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(comment="Код")
    name: Mapped[Optional[str]] = mapped_column(comment="Наименование")
    description: Mapped[Optional[str]] = mapped_column(comment="Описание")


class DicOrderType(BasestModel):
    __tablename__ = "dic_order_type"
    __table_args__ = dict(schema="orders", comment="Типы поручении")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(comment="Код")
    name: Mapped[Optional[str]] = mapped_column(comment="Наименование")


class DicRiskDegree(BasestModel):
    __tablename__ = "dic_risk_degree"
    __table_args__ = dict(schema="orders", comment="Степени риска")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(comment="Код")
    name: Mapped[Optional[str]] = mapped_column(comment="Наименование")


class DicRiskName(BasestModel):
    __tablename__ = "dic_risk_name"
    __table_args__ = dict(schema="orders", comment="Наименования риска")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(comment="Код")
    name: Mapped[Optional[str]] = mapped_column(comment="Наименование")


class DicRiskType(BasestModel):
    __tablename__ = "dic_risk_type"
    __table_args__ = dict(schema="orders", comment="Типы риска")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(comment="Код")
    name: Mapped[Optional[str]] = mapped_column(comment="Наименование")


class Risks(BasestModel):
    __tablename__ = "risks"
    __table_args__ = dict(schema="orders", comment="Риски")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    risk_type: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.dic_risk_type.id"), comment="Тип риска"
    )
    risk_name: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.dic_risk_name.id"), comment="Наименование риска"
    )
    risk_date: Mapped[Optional[date]] = mapped_column(comment="Дата риска")
    risk_degree: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.dic_risk_degree.id"), comment="Степень риска"
    )
    risk_value: Mapped[Optional[float]] = mapped_column(comment="Значение риска")
    risk_details: Mapped[Optional[str]] = mapped_column(comment="Детали риска")
    order_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.orders.id"), comment="ID поручения"
    )
    exec_id: Mapped[Optional[int]] = mapped_column(comment="ID исполнения")
    is_ordered: Mapped[Optional[bool]] = mapped_column(comment="Назначен")
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), comment="Организация"
    )
    period: Mapped[Optional[str]] = mapped_column(comment="Период")

    # Relationships
    risk_type_ref: Mapped[Optional["DicRiskType"]] = relationship(
        "DicRiskType", lazy="selectin", foreign_keys=[risk_type]
    )
    risk_name_ref: Mapped[Optional["DicRiskName"]] = relationship(
        "DicRiskName", lazy="selectin", foreign_keys=[risk_name]
    )
    risk_degree_ref: Mapped[Optional["DicRiskDegree"]] = relationship(
        "DicRiskDegree", lazy="selectin", foreign_keys=[risk_degree]
    )

    # Relationship с поручением
    order: Mapped[Optional["Orders"]] = relationship(
        "Orders", back_populates="risks", foreign_keys=[order_id]
    )


class Orders(BasestModel):
    __tablename__ = "orders"
    __table_args__ = dict(schema="orders", comment="Поручения")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    order_date: Mapped[date] = mapped_column(comment="Дата поручения", nullable=False)
    order_deadline: Mapped[Optional[date]] = mapped_column(
        comment="Срок исполнения", nullable=True
    )
    order_num: Mapped[Optional[int]] = mapped_column(
        comment="Номер поручения", nullable=True
    )
    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admin.employees.id"), comment="Сотрудник", nullable=True
    )
    order_status: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.dic_order_status.id"),
        comment="Статус поручения",
        nullable=True,
    )
    order_type: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.dic_order_type.id"), comment="Тип поручения", nullable=True
    )
    order_desc: Mapped[Optional[str]] = mapped_column(
        Text, comment="Описание поручения", nullable=True
    )
    step_count: Mapped[Optional[int]] = mapped_column(
        comment="Количество шагов", nullable=True
    )
    sign: Mapped[Optional[str]] = mapped_column(comment="Подпись", nullable=True)

    # Relationships
    order_status_ref: Mapped[Optional["DicOrderStatus"]] = relationship(
        "DicOrderStatus", lazy="selectin", foreign_keys=[order_status]
    )
    order_type_ref: Mapped[Optional["DicOrderType"]] = relationship(
        "DicOrderType", lazy="selectin", foreign_keys=[order_type]
    )

    # Relationship с рисками
    risks: Mapped[List["Risks"]] = relationship(
        "Risks", back_populates="order", foreign_keys="Risks.order_id", lazy="selectin"
    )

    # Relationship с сотрудником
    employee: Mapped[Optional["Employees"]] = relationship(
        "app.modules.admins.models.Employees",
        lazy="selectin",
        foreign_keys=[employee_id],
    )


class Executions(BasestModel):
    __tablename__ = "executions"
    __table_args__ = dict(schema="orders", comment="Исполнения")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exec_date: Mapped[Optional[date]] = mapped_column(comment="Дата исполнения")
    exec_text: Mapped[Optional[str]] = mapped_column(Text, comment="Текст исполнения")
    order_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.orders.id"), comment="ID поручения"
    )
    exec_num: Mapped[Optional[int]] = mapped_column(comment="Номер исполнения")
    employee_id: Mapped[Optional[int]] = mapped_column(comment="ID сотрудника")
    is_accepted: Mapped[Optional[bool]] = mapped_column(comment="Принято")
    sign: Mapped[Optional[str]] = mapped_column(Text, comment="Подпись")

    # Relationship to order
    order: Mapped["Orders"] = relationship(
        "Orders", lazy="selectin", foreign_keys=[order_id]
    )


class ExecFiles(BasestModel):
    __tablename__ = "exec_files"
    __table_args__ = dict(schema="orders", comment="Файлы исполнений")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(comment="Название файла")
    file_name: Mapped[Optional[str]] = mapped_column(comment="Имя файла")
    exec_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.executions.id", ondelete="CASCADE"), comment="ID исполнения"
    )
    created: Mapped[Optional[datetime]] = mapped_column(
        comment="Дата создания", default=datetime.utcnow
    )
    ext: Mapped[Optional[str]] = mapped_column(comment="Расширение файла")
    type: Mapped[Optional[int]] = mapped_column(comment="Тип файла")
    length: Mapped[Optional[int]] = mapped_column(comment="Размер файла")
    path: Mapped[Optional[str]] = mapped_column(comment="Путь к файлу")

    # Relationship to execution
    execution: Mapped["Executions"] = relationship(
        "Executions", lazy="selectin", foreign_keys=[exec_id]
    )
