from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.database import engine, Base, AsyncSessionLocal
from src.routers.auth import auth_router
from src.routers.events import event_router
from src.scripts.seed_bookings import seed_bookings
from src.scripts.seed_events import seed_events
from src.scripts.seed_users import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_users(session)
        await seed_events(session)
        await seed_bookings(session)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"msg": "Server is running!"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(event_router, tags=["Event"])
