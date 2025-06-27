from __future__ import annotations

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.common.models import BasestModel


class MineralsLocContracts(BasestModel):
    __tablename__ = "minerals_loc_contracts"
    __table_args__ = dict(schema="ext", comment="Минералс лицензии")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bin: Mapped[str] = mapped_column(comment="БИН")
    name: Mapped[str] = mapped_column(comment="Наименование")
    locnumber: Mapped[str] = mapped_column(comment="Номер лицензии")
    field_5: Mapped[str] = mapped_column()

    geom: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )
