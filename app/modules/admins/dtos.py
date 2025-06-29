from typing import Optional
from datetime import datetime
from app.modules.common.dto import BaseDto, BasestDto


class DicUlDto(BasestDto):
    id: int
    ul_bin: Optional[str] = None
    ul_shortname: Optional[str] = None
    ul_name: Optional[str] = None
    territories_id: Optional[int] = None
    ul_created_at: Optional[datetime] = None


class DicRolesDto(BasestDto):
    id: int
    role_name: Optional[str] = None
    actions: Optional[int] = None
    description: Optional[str] = None


class DicFlDto(BasestDto):
    id: int
    fl_iin: Optional[str] = None
    fl_surname: Optional[str] = None
    fl_name: Optional[str] = None
    fl_patronomic: Optional[str] = None
    phone: Optional[str] = None
    fl_created_at: Optional[datetime] = None


class EmployeesDto(BasestDto):
    id: int
    fl_id: Optional[int] = None
    ul_id: Optional[int] = None
    role_id: Optional[int] = None
    login: Optional[str] = None
    password_hash: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None
    blocked_at: Optional[datetime] = None
    blocked_reason: Optional[str] = None
    joined_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    left_at: Optional[datetime] = None

    # Relationships
    fl: Optional[DicFlDto] = None
    ul: Optional[DicUlDto] = None
    role: Optional[DicRolesDto] = None
