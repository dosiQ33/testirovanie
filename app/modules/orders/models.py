from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

from app.modules.common.models import BasestModel
from app.modules.ckf.models import Organizations


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
    order_id: Mapped[Optional[int]] = mapped_column(comment="ID поручения")
    exec_id: Mapped[Optional[int]] = mapped_column(comment="ID исполнения")
    is_ordered: Mapped[Optional[bool]] = mapped_column(comment="Назначен")
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), comment="Организация"
    )
    period: Mapped[Optional[str]] = mapped_column(comment="Период")

    # Relationships
    organization: Mapped["Organizations"] = relationship(
        "Organizations", lazy="selectin"
    )
    risk_type_ref: Mapped["DicRiskType"] = relationship(
        "DicRiskType", lazy="selectin", foreign_keys=[risk_type]
    )
    risk_name_ref: Mapped["DicRiskName"] = relationship(
        "DicRiskName", lazy="selectin", foreign_keys=[risk_name]
    )
    risk_degree_ref: Mapped["DicRiskDegree"] = relationship(
        "DicRiskDegree", lazy="selectin", foreign_keys=[risk_degree]
    )
