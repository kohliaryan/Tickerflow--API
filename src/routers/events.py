from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.database import get_db
from src.deps.auth import get_current_admin
from src.models import Event, User
from src.schemas.schemas import EventRequestSchema, EventResponseSchema, EventUpdateSchema

event_router = APIRouter()

@event_router.get("/events", response_model=list[EventResponseSchema])
async def get_events(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Event))
    events = result.scalars().all()

    return events

@event_router.get("/event/{event_id}", response_model=EventResponseSchema)
async def get_event(event_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id==event_id))
    event = result.scalars().one_or_none()
    if event is None:
        raise HTTPException(status_code=400, detail="Invalid event id")
    return event

@event_router.post(
    "/events",
    status_code=status.HTTP_201_CREATED,
    response_model=EventResponseSchema
)
async def add_event(
    data: EventRequestSchema,
    db: AsyncSession=Depends(get_db),
    admin: User=Depends(get_current_admin)
):
    new_event = Event(title=data.title, total_tickets=data.total_tickets, available_tickets=data.total_tickets, event_date=data.event_date)

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event

@event_router.put("/event/{event_id}", response_model=EventResponseSchema)
async def update_route(
        event_id: int,
        data: EventUpdateSchema,
        db: AsyncSession=Depends(get_db),
        admin: User=Depends(get_current_admin),
):
    result = await db.execute(select(Event).where(Event.id==event_id))
    event = result.scalars().one_or_none()

    if event is None:
        raise HTTPException(status_code=400, detail="Invalid event id")

    event.title = data.title
    event.event_date = data.event_date

    await  db.commit()
    await db.refresh(event)

    return event
