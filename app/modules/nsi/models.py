from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.common.models import BaseModel, BasestModel, str_uniq
# from app.modules.main.models import Organizations, RiskInfos


class Ugds(BasestModel):
    __tablename__ = "ugds"
    __table_args__ = dict(comment="Справочник УГД")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    parent_id: Mapped[int] = mapped_column(ForeignKey("ugds.id"), comment="Родитель", nullable=True)
    parent: Mapped["Ugds"] = relationship("Ugds", lazy="selectin")

    code: Mapped[str_uniq] = mapped_column(comment="Код УГД")
    name: Mapped[str] = mapped_column(comment="Наименование УГД")
    kato: Mapped[str] = mapped_column(comment="КАТО", nullable=True)

    oblast_id: Mapped[int] = mapped_column(Integer, comment="ID области", nullable=True)
    raion_id: Mapped[int] = mapped_column(Integer, comment="ID района", nullable=True)

    # organizations: Mapped[list["Organizations"]] = relationship(back_populates="ugd", lazy="selectin")
    # risk_infos: Mapped[list["RiskInfos"]] = relationship(back_populates="ugd", lazy="selectin")


class OkedsOld(BaseModel):
    __table_args__ = dict(comment="Справочник ОКЕД")

    code: Mapped[str] = mapped_column(comment="Код ОКЕД")
    name: Mapped[str] = mapped_column(comment="ОКЕД")

    # organizations: Mapped[list["Organizations"]] = relationship(back_populates="oked", lazy="selectin")


class TaxRegimes(BaseModel):
    __table_args__ = dict(comment="Режимы налогообложения")

    name: Mapped[str] = mapped_column(comment="Наименование")

    # organizations: Mapped[list["Organizations"]] = relationship(back_populates="tax_regime", lazy="selectin")


class RegTypes(BaseModel):
    __table_args__ = dict(comment="Типы регистрации")

    name: Mapped[str] = mapped_column(comment="Наименование")

    # organizations: Mapped[list["Organizations"]] = relationship(back_populates="reg_type", lazy="selectin")


class RiskDegrees(BaseModel):
    __table_args__ = dict(comment="Степени риска")

    name: Mapped[str] = mapped_column(comment="Наименование")

    # risk_infos: Mapped[list["RiskInfos"]] = relationship(back_populates="risk_degree", lazy="selectin")
