from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel, BaseModel
from datetime import date

db_schema = 'ckl'


class Cargos(BaseModel):
    __tablename__ = 'cargos'
    __table_args__ = dict(schema=db_schema)

    customs_document_id: Mapped[int] = mapped_column(ForeignKey('ckl.customs_documents.id'), comment='Таможенный документ', nullable=False)
    description: Mapped[str] = mapped_column(name='description', comment='Описание груза', nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('ckl.cargo_types.id'), comment='Тип груза', nullable=False)
    weight_kg: Mapped[float] = mapped_column(name='weight_kg', comment='Вес груза в килограммах', nullable=False)
    volume_m3: Mapped[float] = mapped_column(name='volume_m3', comment='Объем груза в кубических метрах', nullable=False)
    net_weight: Mapped[float] = mapped_column(name='net_weight', comment='Вес нетто', nullable=False)
    gross_weight: Mapped[float] = mapped_column(name='gross_weight', comment='Вес брутто', nullable=False)
    package_type_id: Mapped[int] = mapped_column(ForeignKey('ckl.package_types.id'), comment='Тип упаковки', nullable=False)
    temperature_mode: Mapped[str] = mapped_column(name='temperature_mode', comment='Температурный режим хранения', nullable=True)
    is_dangerous: Mapped[bool] = mapped_column(name='is_dangerous', comment='Опасный груз', nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey('ckl.senders_recipients.id'), comment='Ссылка на отправителя (cargo_senders)', nullable=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey('ckl.senders_recipients.id'), comment='Ссылка на получателя (cargo_receivers)', nullable=True)
    tn_ved_id: Mapped[int] = mapped_column(ForeignKey('ckl.tn_ved.id'), comment='Ссылка на ТНВЭД', nullable=True)
    count: Mapped[int] = mapped_column(name='count', comment='Количество товара', nullable=True)
