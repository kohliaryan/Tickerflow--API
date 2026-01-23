from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

import os

# 1️⃣ Database URL (Postgres + async driver)


DATABASE_URL = os.getenv("DATABASE_URL")

# 2️⃣ Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

# 3️⃣ Base class for models
class Base(DeclarativeBase):
    pass

# 4️⃣ Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 5️⃣ Dependency to get DB session (THIS replaces inventory)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session