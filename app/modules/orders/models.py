from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey, BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from geoalchemy2 import Geometry, WKBElement

from app.modules.common.models import BaseModel, BasestModel


class OrdersOrganizations(BaseModel):
    __tablename__ = "organizations"
    __table_args__ = dict(schema="public", comment="Организации")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin_bin: Mapped[str] = mapped_column(comment="ИИН/БИН", nullable=False)
    name_ru: Mapped[str] = mapped_column(comment="Наименование РУС", nullable=False)
    name_kk: Mapped[Optional[str]] = mapped_column(
        comment="Наименование КАЗ", nullable=True
    )

    date_start: Mapped[Optional[date]] = mapped_column(
        comment="Дата регистрации", nullable=True
    )
    date_stop: Mapped[Optional[date]] = mapped_column(
        comment="Дата снятия с регистрации", nullable=True
    )

    nds_number: Mapped[Optional[int]] = mapped_column(
        comment="Номер свидетельства НДС", nullable=True
    )
    nds_date_reg: Mapped[Optional[str]] = mapped_column(
        comment="Дата регистрации НДС", nullable=True
    )

    address: Mapped[Optional[str]] = mapped_column(comment="Адрес", nullable=True)

    shape: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )

    ugd_id: Mapped[int] = mapped_column(comment="УГД", nullable=False)
    oked_id: Mapped[Optional[int]] = mapped_column(comment="ОКЭД", nullable=True)
    tax_regime_id: Mapped[Optional[int]] = mapped_column(
        comment="Режим налогообложения", nullable=True
    )
    reg_type_id: Mapped[Optional[int]] = mapped_column(
        comment="Тип регистрации", nullable=True
    )
    leader_id: Mapped[Optional[int]] = mapped_column(
        comment="Руководитель", nullable=True
    )

    knn: Mapped[Optional[float]] = mapped_column(
        comment="Коэффициент налоговой нагрузки", nullable=True
    )
    knn_co: Mapped[Optional[float]] = mapped_column(
        comment="Коэффициент СО", nullable=True
    )


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
    risk_type_ref: Mapped["DicRiskType"] = relationship(
        "DicRiskType", lazy="selectin", foreign_keys=[risk_type]
    )
    risk_name_ref: Mapped["DicRiskName"] = relationship(
        "DicRiskName", lazy="selectin", foreign_keys=[risk_name]
    )
    risk_degree_ref: Mapped["DicRiskDegree"] = relationship(
        "DicRiskDegree", lazy="selectin", foreign_keys=[risk_degree]
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
        comment="Сотрудник", nullable=True
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

    order_status_ref: Mapped["DicOrderStatus"] = relationship(
        "DicOrderStatus", lazy="selectin", foreign_keys=[order_status]
    )
    order_type_ref: Mapped["DicOrderType"] = relationship(
        "DicOrderType", lazy="selectin", foreign_keys=[order_type]
    )
