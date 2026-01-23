from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.database import engine, Base
from src.routers.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"msg": "Server is running!"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
