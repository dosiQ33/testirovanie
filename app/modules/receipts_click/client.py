import clickhouse_connect
from clickhouse_connect.driver import Client
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from loguru import logger

from app.config import settings


class ClickHouseClient:
    """ClickHouse client wrapper"""

    def __init__(self):
        self._client: Client | None = None

    def get_client(self) -> Client:
        """Get ClickHouse client instance"""
        if self._client is None:
            try:
                logger.info(f"Attempting to connect to ClickHouse:")
                logger.info(f"  Host: {settings.CLICKHOUSE_HOST}")
                logger.info(f"  Port: {settings.CLICKHOUSE_PORT}")
                logger.info(f"  User: {settings.CLICKHOUSE_USER}")
                logger.info(f"  Database: {settings.CLICKHOUSE_DATABASE}")
                logger.info(f"  Secure: {settings.CLICKHOUSE_SECURE}")

                self._client = clickhouse_connect.get_client(
                    host=settings.CLICKHOUSE_HOST,
                    port=settings.CLICKHOUSE_PORT,
                    username=settings.CLICKHOUSE_USER,
                    password=settings.CLICKHOUSE_PASSWORD,
                    database=settings.CLICKHOUSE_DATABASE,
                    secure=settings.CLICKHOUSE_SECURE,
                    connect_timeout=10,
                    send_receive_timeout=60,
                )
                logger.info(
                    f"Successfully connected to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
                )
            except Exception as e:
                logger.error(f"Failed to connect to ClickHouse: {e}")
                logger.error(
                    f"Connection details: {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
                )
                raise

        return self._client

    def close(self):
        """Close ClickHouse connection"""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("ClickHouse connection closed")


clickhouse_client = ClickHouseClient()


@asynccontextmanager
async def get_clickhouse_client() -> AsyncGenerator[Client, None]:
    """
    Dependency for getting ClickHouse client in FastAPI routes

    Usage:
        async def my_endpoint(client: Client = Depends(get_clickhouse_client)):
            # use client
    """
    client = clickhouse_client.get_client()
    try:
        yield client
    except Exception as e:
        logger.error(f"ClickHouse operation failed: {e}")
        raise
    finally:
        pass


def get_clickhouse_client_sync() -> Client:
    """Синхронная версия для использования в зависимостях"""
    return clickhouse_client.get_client()
