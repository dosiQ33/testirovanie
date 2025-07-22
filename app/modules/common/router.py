"""
Project: nam
Created Date: Monday February 3rd 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, HTTPException
from typing import List, Type, TypeVar, Generic
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_cache.decorator import cache
from starlette.requests import Request
from starlette.responses import Response
from typing import Any
import orjson
from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder
from app.database.deps import get_session_with_commit
from sqlalchemy.orm import class_mapper

T = TypeVar("T", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int
    total: int
    page_count: int


# Определяем TTL кэша в зависимости от окружения
PROJECT_ENV = os.getenv("PROJECT_ENV")
cache_ttl = 1 * 60 * 60 if PROJECT_ENV == "prod" or PROJECT_ENV == "test" else 1


def request_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response: Response = None,
    **kwargs,
):
    return ":".join([namespace, request.method.lower(), request.url.path, repr(sorted(request.query_params.items()))])


def to_dict(obj):
    """
    Serialize SQLAlchemy object to dictionary, including relationships.
    """

    def serialize(value):
        if isinstance(value, list):
            return [to_dict(item) for item in value]
        elif hasattr(value, "__dict__"):
            return to_dict(value)
        return value

    serialized_data = {}
    for prop in class_mapper(obj.__class__).iterate_properties:
        if hasattr(prop, "key"):
            key = prop.key
            value = getattr(obj, key)
            serialized_data[key] = serialize(value)
    return serialized_data


class ORJsonCoder(Coder):
    @classmethod
    def encode(cls, value: Any):
        # Ensure value is serializable before caching to avoid SQLAlchemy async errors
        if isinstance(value, list):
            value = [item.model_dump() if isinstance(item, BaseModel) else item.to_dict() for item in value]
        elif isinstance(value, BaseModel):
            value = value.model_dump()

        if isinstance(value, bytes):
            # If the value is already bytes, return it as is
            return value

        serialized = orjson.dumps(value, default=jsonable_encoder)
        return serialized

    @classmethod
    def decode(cls, value: bytes) -> Any:
        return orjson.loads(value)


class BaseCRUDRouter(APIRouter, Generic[T]):
    dto: Type[T]

    def __init__(self, prefix: str, model: Type[BaseModel], repo: Type, dto: Type[T], filter_class: type = None, tags=None):
        super().__init__(tags=tags)

        self.model = model
        self.repo = repo
        self.dto = dto
        self.filter_class = filter_class

        sub_router = APIRouter(prefix=f"/{prefix}" if prefix else "")

        sub_router.get("/count", response_model=int)(self.count)

        sub_router.get("/{id}", response_model=dto)(self.get_one)

        if filter_class:
            sub_router.get("", response_model=PaginatedResponse[dto])(self.get_many_with_common_filters)
        else:
            sub_router.get("", response_model=PaginatedResponse[T] | List[T])(self.get_many)

        self.include_router(sub_router)

    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_one(self, id: int, session: AsyncSession = Depends(get_session_with_commit)) -> T:
        response = await self.repo(session).get_one_by_id(id)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")

        return self.dto.model_validate(response)

    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_many(
        self,
        page_size: int | None = None,
        page: int | None = None,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> PaginatedResponse[T] | List[T]:
        records, total = await self.repo(session).get_many(page_size=page_size, page=page)
        current_page = page or 1
        total_pages = (total // page_size + int(total % page_size > 0)) if page_size else 1

        if page_size is None:
            # If no page size is provided, return all records without pagination
            return [self.dto.model_validate(item) for item in records]

        return PaginatedResponse[T](
            data=[self.dto.model_validate(item) for item in records],
            page=current_page,
            total=total,
            page_count=total_pages,
        )

    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def get_many_with_common_filters(
        self,
        filters: Filter | None = None,
        page_size: int | None = None,
        page: int | None = None,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> PaginatedResponse[T]:
        """
        Получить список записей с поддержкой фильтрации и пагинации.

        - **filters**: параметры фильтрации, зависят от модели, смотри тут [https://fastapi-filter.netlify.app](https://fastapi-filter.netlify.app)
        - **page_size**: размер страницы
        - **page**: номер страницы
        - **BODY** ПУСТОЙ, GET же метод ))) потом разберусь как убрать из сваррера
        """
        if self.filter_class and filters:
            filters = FilterDepends(self.filter_class)

        records, total = await self.repo(session).get_many(filters=filters, page_size=page_size, page=page)
        current_page = page or 1
        total_pages = (total // page_size + int(total % page_size > 0)) if page_size else 1

        return PaginatedResponse[T](
            data=[self.dto.model_validate(item, from_attributes=True) for item in records],
            page=current_page,
            total=total,
            page_count=total_pages,
        )

    @cache(expire=cache_ttl, key_builder=request_key_builder)  # Кэширование на 24 часа
    async def count(
        self,
        filters: Filter | None = None,
        session: AsyncSession = Depends(get_session_with_commit),
    ) -> int:
        """
        Получить количество записей с поддержкой фильтрации

        - **filters**: параметры фильтрации, зависят от модели, смотри тут [https://fastapi-filter.netlify.app](https://fastapi-filter.netlify.app)
        """
        if self.filter_class and filters:
            filters = FilterDepends(self.filter_class)

        count = await self.repo(session).count(filters=filters)

        return count


class BaseExtRouter(APIRouter, Generic[T]):
    dto: Type[T]

    def __init__(self, prefix: str, model: Type[BaseModel], repo: Type, dto: Type[T], tags=None):
        super().__init__(tags=tags)

        self.model = model
        self.repo = repo
        self.dto = dto

        sub_router = APIRouter(prefix=f"/{prefix}" if prefix else "")

        sub_router.get("/parent/{parent_id}", response_model=List[dto])(self.get_by_parent_id)
        sub_router.get("/{id}", response_model=dto)(self.get_one_by_id)
        sub_router.get("", response_model=List[dto])(self.get_many)

        self.include_router(sub_router)

    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_one_by_id(self, id: int, session: AsyncSession = Depends(get_session_with_commit)) -> T:
        response = await self.repo(session).get_one_by_id(id)
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")

        return self.dto.model_validate(response)

    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_many(self, session: AsyncSession = Depends(get_session_with_commit)) -> List[T]:
        return await self.repo(session).get_many()

    @cache(expire=cache_ttl, key_builder=request_key_builder, coder=ORJsonCoder)  # Кэширование на 24 часа
    async def get_by_parent_id(self, parent_id: int, session: AsyncSession = Depends(get_session_with_commit)) -> List[T]:
        return await self.repo(session).get_by_parent_id(parent_id)
