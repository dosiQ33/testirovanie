"""
Project: nam
Created Date: Thursday January 30th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

import json
import re
from functools import partial
from typing import Any, List, Optional, Annotated
from geoalchemy2.shape import to_shape
from shapely import to_geojson, wkb
from sqlmodel import SQLModel
from starlette.responses import JSONResponse
from pydantic import PlainSerializer
from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy.ext.declarative import DeclarativeMeta
from geoalchemy2.elements import WKBElement
from binascii import unhexlify

# CONSTANTS
_snake_1 = partial(re.compile(r"(.)((?<![^A-Za-z])[A-Z][a-z]+)").sub, r"\1_\2")
_snake_2 = partial(re.compile(r"([a-z0-9])([A-Z])").sub, r"\1_\2")


def snake_case(string: str) -> str:
    return _snake_2(_snake_1(string)).casefold()


class ErrorDetail(SQLModel):
    type: Optional[str] = "general"
    description: str
    field: Optional[str] = None


class ErrorMessage(SQLModel):
    error_code: str
    detail: List[ErrorDetail]


def prettylog(data: Any) -> None:
    print("#" * 80)
    print(data)
    print("#" * 80)


def prettylogjson(data: Any) -> None:
    print("#" * 80)
    print(json.dumps(data, indent=2, default=str))
    print("#" * 80)


def throw_error(error_code: str, detail: List[ErrorDetail] | ErrorDetail, http_code: int = 500):
    if isinstance(detail, list):
        return JSONResponse(
            ErrorMessage(error_code=error_code, detail=detail).model_dump(),
            status_code=http_code,
        )
    else:
        _detail = ErrorDetail(type="general", description=detail, field=None)
        return JSONResponse(
            ErrorMessage(error_code=error_code, detail=[_detail]).model_dump(),
            status_code=http_code,
        )


def wkb_to_geojson(value):
    """Convert WKBElement(bytes) to GeoJSON"""
    if not value:
        return None

    if isinstance(value, WKBElement):
        return json.loads(to_geojson(to_shape(value)))

    if isinstance(value, str):
        # value is in HEX format
        binary = unhexlify(value)
        shapely_instance = wkb.loads(binary)

        return json.loads(to_geojson(shapely_instance))

    return None


SerializedGeojson = Annotated[object, PlainSerializer(wkb_to_geojson)]
"""WKBElemnt serialized to GeoJSON"""


def shape_to_geojson(obj):
    obj.shape = ST_AsGeoJSON(obj.shape)
    return obj


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # Convert SQLAlchemy model to dictionary
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith("_") and x != "metadata"]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)
