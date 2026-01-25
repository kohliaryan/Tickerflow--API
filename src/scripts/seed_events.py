from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event

events = [
    {
        "title": "Harkirat Sangha Live - Earth to Mars",
        "total_tickets": 1000,
        "price_in_rupee": 1500,
        "venue": "Downtown 44, Pathankot, Punjab",
        "event_date": "2026-02-14T12:30:00.014Z",
    },
    {
        "title": "Sidhu Moosewala Tribute Night",
        "total_tickets": 800,
        "price_in_rupee": 1200,
        "venue": "Ivy Hospital Grounds, Mohali, Punjab",
        "event_date": "2026-03-01T14:00:00.000Z",
    },
    {
        "title": "Diljit Dosanjh Live – Born To Shine Tour",
        "total_tickets": 1500,
        "price_in_rupee": 2500,
        "venue": "Sector 17 Parade Ground, Chandigarh",
        "event_date": "2026-03-20T13:00:00.000Z",
    },
    {
        "title": "AP Dhillon Brownprint Tour",
        "total_tickets": 1200,
        "price_in_rupee": 2200,
        "venue": "GNDU Open Air Theatre, Amritsar, Punjab",
        "event_date": "2026-04-05T15:30:00.000Z",
    },
    {
        "title": "Punjabi Indie Night – Local Legends",
        "total_tickets": 500,
        "price_in_rupee": 800,
        "venue": "Rose Garden, Ludhiana, Punjab",
        "event_date": "2026-04-18T16:00:00.000Z",
    },
]

async def seed_events(db: AsyncSession):
    result = await db.execute(select(Event))
    existing_events = result.scalars().first()

    if existing_events is not None:
        return

    for event in events:
        e = Event(
            title=event["title"],
            total_tickets=event["total_tickets"],
            available_tickets= event["total_tickets"],
            price_in_rupee=event["price_in_rupee"],
            venue=event["venue"],
            event_date=datetime.fromisoformat(
                event["event_date"].replace("Z", "+00:00")
            ),
        )
        db.add(e)
    await db.commit()

