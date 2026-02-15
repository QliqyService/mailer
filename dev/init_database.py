import asyncio

import asyncpg
from loguru import logger as LOGGER

from app.logger import CustomLogger
from app.settings import get_settings


class FixtureManager:
    def __init__(self):
        self.config = get_settings()
        self.logger = CustomLogger.make_logger()

    def get_postgres_dsn(self) -> str:
        """Generate a DSN for connecting to the PostgreSQL database."""
        return "postgresql://{}:{}@{}:{}/postgres".format(
            self.config.POSTGRES_USER,
            self.config.POSTGRES_PASSWORD,
            self.config.POSTGRES_HOST,
            self.config.POSTGRES_PORT,
        )

    async def init_database(self):
        """Create a database with context manager and add permissions to the current user."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"CREATE DATABASE {self.config.POSTGRES_DB}")
                    await conn.execute(
                        f"GRANT ALL PRIVILEGES ON DATABASE {self.config.POSTGRES_DB} TO {self.config.POSTGRES_USER}"
                    )
                    LOGGER.warning(f"Database created '{self.config.POSTGRES_DB}', permissions have been granted.")
        except asyncpg.exceptions.DuplicateDatabaseError:
            LOGGER.warning(f"Database '{self.config.POSTGRES_DB}' already exists.")

    async def drop_database(self):
        """Drop database."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"DROP DATABASE {self.config.POSTGRES_DB}")
                    LOGGER.warning(f"Database dropped '{self.config.POSTGRES_DB}'")
        except Exception as e:
            LOGGER.warning(f"Database '{self.config.POSTGRES_DB}' drop failed: {e}.")

def main_init() -> None:
    app = FixtureManager()
    asyncio.run(app.init_database())


def main_drop() -> None:
    app = FixtureManager()
    asyncio.run(app.drop_database())
