from clickhouse_connect.driver import Client
from fastapi import Depends

from .client import get_clickhouse_client_sync


def get_clickhouse_client() -> Client:
    """
    FastAPI dependency for getting ClickHouse client

    Usage:
        async def my_endpoint(client: Client = Depends(get_clickhouse_client)):
            # use client
    """
    return get_clickhouse_client_sync()
