"""
Project: nam
Created Date: Monday February 3rd 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from typing import Optional
from pydantic import Field

from app.modules.common.dto import BaseDto


class CommonRefDto(BaseDto):
    code: str = Field()
    name: str = Field()


class SimpleRefDto(BaseDto):
    name: str = Field()


class UgdsDto(BaseDto):
    code: str = Field()
    name: str = Field()

    parent_id: Optional[int] = None

    kato: Optional[str] = None
    oblast_id: Optional[int] = None
    raion_id: Optional[int] = None
