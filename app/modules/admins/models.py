from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey, BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.modules.common.models import BasestModel


class DicUl(BasestModel):
    __tablename__ = "dic_ul"
    __table_args__ = dict(schema="admin", comment="Справочник юридических лиц")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ul_bin: Mapped[Optional[str]] = mapped_column(comment="БИН")
    ul_shortname: Mapped[Optional[str]] = mapped_column(comment="Краткое наименование")
    ul_name: Mapped[Optional[str]] = mapped_column(comment="Полное наименование")
    territories_id: Mapped[Optional[int]] = mapped_column(comment="ID территории")
    ul_created_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата создания")


class DicRoles(BasestModel):
    __tablename__ = "dic_roles"
    __table_args__ = dict(schema="admin", comment="Справочник ролей")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role_name: Mapped[Optional[str]] = mapped_column(comment="Название роли")
    actions: Mapped[Optional[int]] = mapped_column(comment="Действия")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="Описание")


class DicFl(BasestModel):
    __tablename__ = "dic_fl"
    __table_args__ = dict(schema="admin", comment="Справочник физических лиц")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fl_iin: Mapped[Optional[str]] = mapped_column(comment="ИИН")
    fl_surname: Mapped[Optional[str]] = mapped_column(comment="Фамилия")
    fl_name: Mapped[Optional[str]] = mapped_column(comment="Имя")
    fl_patronomic: Mapped[Optional[str]] = mapped_column(comment="Отчество")
    phone: Mapped[Optional[str]] = mapped_column(comment="Телефон")
    fl_created_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата создания")


class Employees(BasestModel):
    __tablename__ = "employees"
    __table_args__ = dict(schema="admin", comment="Сотрудники")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fl_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admin.dic_fl.id"), comment="Физическое лицо"
    )
    ul_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admin.dic_ul.id"), comment="Юридическое лицо"
    )
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admin.dic_roles.id"), comment="Роль"
    )
    login: Mapped[Optional[str]] = mapped_column(comment="Логин")
    password_hash: Mapped[Optional[str]] = mapped_column(comment="Хеш пароля")
    is_active: Mapped[Optional[bool]] = mapped_column(comment="Активен", default=True)
    is_blocked: Mapped[Optional[bool]] = mapped_column(
        comment="Заблокирован", default=False
    )
    blocked_at: Mapped[Optional[datetime]] = mapped_column(comment="Время блокировки")
    blocked_reason: Mapped[Optional[str]] = mapped_column(
        Text, comment="Причина блокировки"
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата присоединения")
    created_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата создания")
    left_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата увольнения")

    # Relationships
    fl: Mapped["DicFl"] = relationship("DicFl", lazy="selectin")
    ul: Mapped["DicUl"] = relationship("DicUl", lazy="selectin")
    role: Mapped["DicRoles"] = relationship("DicRoles", lazy="selectin")
