from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)


from app.config import alembic_database_url


engine = create_async_engine(
    url=alembic_database_url.render_as_string(hide_password=False),
    plugins=["geoalchemy2"],
    pool_size=10,
    max_overflow=15
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
