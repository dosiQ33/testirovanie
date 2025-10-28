from typing import TYPE_CHECKING

from sqlalchemy import Integer, Float, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.common.models import BasestModel

if TYPE_CHECKING:
    from app.modules.ckf.models import Organizations, Kkms


class GtinNp(BasestModel):
    __tablename__ = "gtin_np"
    __table_args__ = dict(schema="public", comment="GTIN по налогоплательщикам")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dtype: Mapped[str] = mapped_column(comment="Тип данных", nullable=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("organizations.id"),
        comment="ID организации",
        nullable=True,
    )
    gtin: Mapped[str] = mapped_column(comment="GTIN код", nullable=True)
    item_name: Mapped[str] = mapped_column(comment="Наименование товара", nullable=True)
    full_price: Mapped[float] = mapped_column(
        Float, comment="Полная цена", nullable=True
    )
    full_count: Mapped[float] = mapped_column(
        Float, comment="Полное количество", nullable=True
    )

    organization: Mapped["Organizations"] = relationship(
        "Organizations", foreign_keys=[org_id], lazy="noload"
    )


class GtinKkms(BasestModel):
    __tablename__ = "gtin_kkms"
    __table_args__ = dict(schema="public", comment="GTIN по ККМ")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dtype: Mapped[str] = mapped_column(comment="Тип данных", nullable=True)
    kkms_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("kkms.id"), comment="ID ККМ", nullable=True
    )
    gtin: Mapped[str] = mapped_column(comment="GTIN код", nullable=True)
    item_name: Mapped[str] = mapped_column(comment="Наименование товара", nullable=True)
    full_price: Mapped[float] = mapped_column(
        Float, comment="Полная цена", nullable=True
    )
    full_count: Mapped[float] = mapped_column(
        Float, comment="Полное количество", nullable=True
    )

    kkm: Mapped["Kkms"] = relationship("Kkms", foreign_keys=[kkms_id], lazy="noload")
