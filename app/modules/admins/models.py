from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey, BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime

from app.modules.common.models import BasestModel


class DicUl(BasestModel):
    __tablename__ = "dic_ul"
    __table_args__ = dict(schema="admin", comment="Справочник юридических лиц")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, comment="Родительский ID"
    )
    bin: Mapped[Optional[str]] = mapped_column(comment="БИН")
    shortname: Mapped[Optional[str]] = mapped_column(comment="Краткое наименование")
    name: Mapped[Optional[str]] = mapped_column(comment="Полное наименование")
    address: Mapped[Optional[str]] = mapped_column(comment="Адрес")
    kato: Mapped[Optional[str]] = mapped_column(comment="КАТО")
    oblast_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="ID области")
    raion_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="ID района")
    create_date: Mapped[Optional[date]] = mapped_column(comment="Дата создания")


class DicRoles(BasestModel):
    __tablename__ = "dic_roles"
    __table_args__ = dict(schema="admin", comment="Справочник ролей")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role_name: Mapped[Optional[str]] = mapped_column(comment="Название роли")
    actions: Mapped[Optional[int]] = mapped_column(Integer, comment="Действия")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="Описание")


class DicFl(BasestModel):
    __tablename__ = "dic_fl"
    __table_args__ = dict(schema="admin", comment="Справочник физических лиц")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    iin: Mapped[Optional[str]] = mapped_column(comment="ИИН")
    surname: Mapped[Optional[str]] = mapped_column(comment="Фамилия")
    name: Mapped[Optional[str]] = mapped_column(comment="Имя")
    patronymic: Mapped[Optional[str]] = mapped_column(comment="Отчество")
    date_of_birth: Mapped[Optional[date]] = mapped_column(comment="Дата рождения")
    email: Mapped[Optional[str]] = mapped_column(Text, comment="Email")
    phone: Mapped[Optional[str]] = mapped_column(comment="Телефон")
    create_date: Mapped[Optional[date]] = mapped_column(comment="Дата создания")


class Employees(BasestModel):
    __tablename__ = "employees"
    __table_args__ = dict(schema="admin", comment="Сотрудники")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fl_id: Mapped[Optional[int]] = mapped_column(Integer, comment="Физическое лицо")
    ul_id: Mapped[Optional[int]] = mapped_column(Integer, comment="Юридическое лицо")
    role: Mapped[Optional[int]] = mapped_column(Integer, comment="Роль")
    login: Mapped[Optional[str]] = mapped_column(comment="Логин")
    password: Mapped[Optional[str]] = mapped_column(comment="Пароль")
    deleted: Mapped[Optional[bool]] = mapped_column(comment="Удален", default=False)
    blocked: Mapped[Optional[bool]] = mapped_column(
        comment="Заблокирован", default=False
    )
    empl_create_date: Mapped[Optional[datetime]] = mapped_column(
        comment="Дата создания сотрудника"
    )
    employee_position: Mapped[Optional[str]] = mapped_column(
        comment="Должность сотрудника"
    )
    employee_department: Mapped[Optional[str]] = mapped_column(
        comment="Отдел сотрудника"
    )
    employee_status: Mapped[Optional[str]] = mapped_column(comment="Статус сотрудника")

    # Relationships
    fl: Mapped["DicFl"] = relationship(
        "DicFl",
        lazy="selectin",
        foreign_keys=[fl_id],
        primaryjoin="Employees.fl_id == DicFl.id",
    )
    ul: Mapped["DicUl"] = relationship(
        "DicUl",
        lazy="selectin",
        foreign_keys=[ul_id],
        primaryjoin="Employees.ul_id == DicUl.id",
    )
    role_ref: Mapped["DicRoles"] = relationship(
        "DicRoles",
        lazy="selectin",
        foreign_keys=[role],
        primaryjoin="Employees.role == DicRoles.id",
    )
