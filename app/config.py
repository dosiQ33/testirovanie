import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import PostgresDsn, computed_field
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/db.sqlite3"
    SECRET_KEY: str
    ALGORITHM: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # ClickHouse settings
    CLICKHOUSE_HOST: str = "coc_db_clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "coc_admin"
    CLICKHOUSE_PASSWORD: str = "QAZqaz123"
    CLICKHOUSE_DATABASE: str = "default"
    CLICKHOUSE_SECURE: bool = False

    @computed_field  # type: ignore[misc]
    @property
    def DB_URL(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER or "coc_admin",
            password=self.POSTGRES_PASSWORD or "QAZqaz123",
            host=self.POSTGRES_HOST or "localhost",
            port=int(self.POSTGRES_PORT) or 5432,
            path=f"/{self.POSTGRES_DB}" or "/coc",
        )

    @computed_field  # type: ignore[misc]
    @property
    def ALEMBIC_DB_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=str(self.POSTGRES_USER) or "coc_admin",
            password=self.POSTGRES_PASSWORD or "QAZqaz123",
            host=self.POSTGRES_HOST or "localhost",
            port=int(self.POSTGRES_PORT) or 5432,
            database=self.POSTGRES_DB or "coc",
        )

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        env_ignore_empty=True,
        extra="ignore",
        env_file_encoding="utf-8",
    )


# Получаем параметры для загрузки переменных среды
settings = Settings()
database_url = settings.DB_URL
alembic_database_url = settings.ALEMBIC_DB_URL
