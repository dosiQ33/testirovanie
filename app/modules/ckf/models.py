from sqlalchemy import BigInteger, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.modules.common.models import BaseModel, BaseModelWithShapePoint, str_uniq
from app.modules.nsi.models import Ugds, TaxRegimes, RegTypes, RiskDegrees
from app.modules.ext.okeds.models import Okeds


class Organizations(BaseModelWithShapePoint):
    __table_args__ = dict(comment="Налогоплательщики")

    iin_bin: Mapped[str_uniq] = mapped_column(comment="ИИН/БИН", nullable=False)
    name_ru: Mapped[str] = mapped_column(comment="Наименование РУС", nullable=False)
    name_kk: Mapped[str] = mapped_column(comment="Наименование КАЗ", nullable=True)

    date_start: Mapped[date] = mapped_column(comment="Дата регистрации", nullable=True)
    date_stop: Mapped[date] = mapped_column(comment="Дата снятия с регистрации", nullable=True)

    """УГД"""
    ugd_id: Mapped[int] = mapped_column(ForeignKey("ugds.id"), comment="УГД", nullable=False)
    ugd: Mapped["Ugds"] = relationship("Ugds", lazy="selectin")

    """ОКЭД"""
    oked_id: Mapped[int] = mapped_column(ForeignKey("ext.okeds.id"), comment="ОКЭД", nullable=True)
    oked: Mapped["Okeds"] = relationship("Okeds", lazy="selectin")

    nds_number: Mapped[str] = mapped_column(comment="Номер свидетельства НДС", nullable=True)
    nds_date_reg: Mapped[date] = mapped_column(comment="Дата регистрации НДС", nullable=True)

    """Режим налогообложения"""
    tax_regime_id: Mapped[int] = mapped_column(ForeignKey("tax_regimes.id"), comment="Режим налогооблажения", nullable=True)
    tax_regime: Mapped["TaxRegimes"] = relationship("TaxRegimes", lazy="selectin")

    """Тип регистрации"""
    reg_type_id: Mapped[int] = mapped_column(ForeignKey("reg_types.id"), comment="Тип регистрации", nullable=False)
    reg_type: Mapped["RegTypes"] = relationship("RegTypes", lazy="selectin")

    """Руководитель"""
    leader_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), comment="Руководитель", nullable=True)
    leader: Mapped["Persons"] = relationship("Persons", lazy="selectin")

    knn: Mapped[float] = mapped_column(comment="Коэффициент налоговой нагрузки", nullable=True)
    knn_co: Mapped[float] = mapped_column(comment="Коэффициент СО - среднеотраслевое значение КНН", nullable=True)

    address: Mapped[str] = mapped_column(comment="Адрес", nullable=True)

    kkms: Mapped[list["Kkms"]] = relationship(back_populates="organization", lazy="selectin")
    risk_info: Mapped["RiskInfos"] = relationship(back_populates="organization", lazy="selectin")

    esf_seller: Mapped["EsfSeller"] = relationship(back_populates="organization", lazy="selectin")
    esf_seller_daily: Mapped["EsfSellerDaily"] = relationship(back_populates="organization", lazy="selectin")
    esf_buyer: Mapped["EsfBuyer"] = relationship(back_populates="organization", lazy="selectin")
    esf_buyer_daily: Mapped["EsfBuyerDaily"] = relationship(back_populates="organization", lazy="selectin")


class RiskInfos(BaseModel):
    __table_args__ = dict(comment="Сведения по рискам налогоплательщиков")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="risk_info", lazy="selectin")

    """Степень риска"""
    risk_degree_id: Mapped[int] = mapped_column(ForeignKey("risk_degrees.id"), comment="Степень риска", nullable=False)
    risk_degree: Mapped["RiskDegrees"] = relationship("RiskDegrees", lazy="selectin")

    calculated_at: Mapped[date] = mapped_column(comment="Дата актуальности степени риска")

    """УГД"""
    ugd_id: Mapped[int] = mapped_column(ForeignKey("ugds.id"), comment="УГД", nullable=False)
    ugd: Mapped["Ugds"] = relationship("Ugds", lazy="selectin")


class Persons(BaseModel):
    __table_args__ = dict(comment="Физические лица")

    iin: Mapped[str_uniq] = mapped_column(comment="ИИН")
    name: Mapped[str] = mapped_column(comment="ФИО")

    organizations: Mapped[list["Organizations"]] = relationship(back_populates="leader", lazy="selectin")


class EsfSeller(BaseModel):
    __table_args__ = dict(comment="ЭСФ реализация за год")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="esf_seller", lazy="selectin")

    total_amount: Mapped[float] = mapped_column(comment="Оборот", nullable=True, default=0)
    nds_amount: Mapped[float] = mapped_column(comment="Оборот НДС", nullable=True, default=0)


class EsfSellerDaily(BaseModel):
    __table_args__ = dict(comment="ЭСФ реализация за 1 день")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="esf_seller_daily", lazy="selectin")

    total_amount: Mapped[float] = mapped_column(comment="Оборот", nullable=True, default=0)
    nds_amount: Mapped[float] = mapped_column(comment="Оборот НДС", nullable=True, default=0)


class EsfBuyer(BaseModel):
    __table_args__ = dict(comment="ЭСФ приобретение за год")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="esf_buyer", lazy="selectin")

    total_amount: Mapped[float] = mapped_column(comment="Оборот", nullable=True, default=0)
    nds_amount: Mapped[float] = mapped_column(comment="Оборот НДС", nullable=True, default=0)


class EsfBuyerDaily(BaseModel):
    __table_args__ = dict(comment="ЭСФ приобретение за 1 день")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="esf_buyer_daily", lazy="selectin")

    total_amount: Mapped[float] = mapped_column(comment="Оборот", nullable=True, default=0)
    nds_amount: Mapped[float] = mapped_column(comment="Оборот НДС", nullable=True, default=0)


class Kkms(BaseModelWithShapePoint):
    __table_args__ = dict(comment="Контрольно-кассовые машины")

    """Организация"""
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), comment="Организация", nullable=False)
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="kkms", lazy="selectin")

    reg_number: Mapped[str] = mapped_column(comment="Регистрационный номер ККМ", nullable=True)

    serial_number: Mapped[str] = mapped_column(comment="Заводской номер ККМ")
    model_name: Mapped[str] = mapped_column(comment="Марка (модель) ККМ")
    made_year: Mapped[str] = mapped_column(comment="Год выпуска")

    date_start: Mapped[date] = mapped_column(comment="Дата регистрации", nullable=True)
    date_stop: Mapped[date] = mapped_column(comment="Дата снятия с регистрации", nullable=True)

    address: Mapped[str] = mapped_column(comment="Адрес")


class Receipts(BaseModel):
    __table_args__ = dict(comment="Чеки")

    """ККМ"""
    kkms_id: Mapped[int] = mapped_column(ForeignKey("kkms.id"), comment="ККМ", nullable=False)
    kkm: Mapped["Kkms"] = relationship("Kkms", lazy="selectin")  # ОСТОРОЖНО!!!

    operation_date: Mapped[datetime] = mapped_column(comment="Дата и время совершения кассовой операции", nullable=True)
    auto_fiskal_mark_check: Mapped[str] = mapped_column(comment="Автономный фискальный номер", nullable=True)
    fiskal_sign: Mapped[int] = mapped_column(BigInteger, comment="Фискальный номер", nullable=True)
    item_name: Mapped[str] = mapped_column(comment="Наименование товара", nullable=True)
    item_price: Mapped[float] = mapped_column(comment="Цена товара", nullable=True)
    item_count: Mapped[float] = mapped_column(comment="Количество товара", nullable=True)
    item_nds: Mapped[float] = mapped_column(comment="НДС", nullable=True)
    full_item_price: Mapped[float] = mapped_column(comment="Итог", nullable=True)
    payment_type: Mapped[int] = mapped_column(comment="Вид оплаты", nullable=True)
    # updated_date: Mapped[datetime] = mapped_column(comment="Дата заливки данных", nullable=True)


class ReceiptsAnnual(BaseModel):
    __table_args__ = dict(comment="Чеки за год")

    """ККМ"""
    kkms_id: Mapped[int] = mapped_column(ForeignKey("kkms.id"), comment="ККМ", nullable=False)
    kkm: Mapped["Kkms"] = relationship("Kkms", lazy="selectin")  # ОСТОРОЖНО!!!

    check_sum: Mapped[float] = mapped_column(comment="Общая сумма", nullable=True)
    check_count: Mapped[int] = mapped_column(comment="Количество чеков", nullable=True)
    year: Mapped[int] = mapped_column(comment="Год", nullable=True)


class ReceiptsDaily(BaseModel):
    __table_args__ = dict(comment="Чеки за день")

    """ККМ"""
    kkms_id: Mapped[int] = mapped_column(ForeignKey("kkms.id"), comment="ККМ", nullable=False)
    kkm: Mapped["Kkms"] = relationship("Kkms", lazy="selectin")  # ОСТОРОЖНО!!!

    check_sum: Mapped[float] = mapped_column(comment="Общая сумма", nullable=True)
    check_count: Mapped[int] = mapped_column(comment="Количество чеков", nullable=True)
    date_check: Mapped[date] = mapped_column(Date, comment="Дата", nullable=True)
