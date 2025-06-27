from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BaseModel, str_uniq
# from app.modules.main.models import Organizations, RiskInfos


class Ugds(BaseModel):
    __table_args__ = dict(comment="Справочник УГД")

    code: Mapped[str_uniq] = mapped_column(comment="Код УГД")
    name: Mapped[str] = mapped_column(comment="Наименование УГД")

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
