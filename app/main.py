from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.modules.ckf.router import router as router_ckf
from app.modules.nsi.router import router as router_nsi
from app.modules.ext.router import router as router_ext
from app.modules.ar.router import router as router_ar
from app.modules.orders.router import router as router_orders
from app.modules.admins.router import router as router_admins
from app.modules.regions.router import router as router_regions
from app.modules.receipts_click.router import router as router_receipts_click


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    redis = aioredis.from_url("redis://coc_redis")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    logger.info("Завершение работы приложения...")


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер

    global_prefix_v1 = "/api/v1"

    root_router = APIRouter(prefix=global_prefix_v1)

    @root_router.get("/", tags=["root"], name="ROOT")
    def home_page():
        return "API works"

    # Подключение роутеров
    app.include_router(root_router, tags=["root"])

    app.include_router(router_ckf, prefix=global_prefix_v1)
    # app.include_router(router_ckl, prefix=global_prefix_v1) # Временно отключен

    app.include_router(router_nsi, prefix=global_prefix_v1)
    app.include_router(router_ext, prefix=global_prefix_v1)
    app.include_router(router_ar, prefix=global_prefix_v1)
    app.include_router(router_orders, prefix=global_prefix_v1)
    app.include_router(router_admins, prefix=global_prefix_v1)
    app.include_router(router_regions, prefix=global_prefix_v1)
    app.include_router(router_receipts_click, prefix=global_prefix_v1)


def create_app() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.

    Returns:
        Сконфигурированное приложение FastAPI
    """
    app = FastAPI(
        title="API ЦКФ и ЦКЛ",
        description=("API ЦКФ и ЦКЛ"),
        version="0.0.1",
        openapi_version="3.1.0",
        lifespan=lifespan,
        docs_url="/apidocs",
        swagger_ui_parameters={"docExpansion": "none"},
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Монтирование статических файлов
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Регистрация роутеров
    register_routers(app)

    return app


# Создание экземпляра приложения
app = create_app()
