from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Booking, User, Event

bookings = [
    # Diljit Dosanjh Live
    {"user_email": "harpreet.singh@test.com", "event_title": "Diljit Dosanjh Live – Born To Shine Tour"},
    {"user_email": "gurleen.kaur@test.com", "event_title": "Diljit Dosanjh Live – Born To Shine Tour"},
    {"user_email": "amanpreet.singh@test.com", "event_title": "Diljit Dosanjh Live – Born To Shine Tour"},
    {"user_email": "navjot.kaur@test.com", "event_title": "Diljit Dosanjh Live – Born To Shine Tour"},
    {"user_email": "simran.kaur@test.com", "event_title": "Diljit Dosanjh Live – Born To Shine Tour"},

    # Sidhu Moosewala Tribute
    {"user_email": "jaspreet.singh@test.com", "event_title": "Sidhu Moosewala Tribute Night"},
    {"user_email": "manpreet.singh@test.com", "event_title": "Sidhu Moosewala Tribute Night"},
    {"user_email": "kiran.kaur@test.com", "event_title": "Sidhu Moosewala Tribute Night"},
    {"user_email": "sandeep.singh@test.com", "event_title": "Sidhu Moosewala Tribute Night"},

    # AP Dhillon
    {"user_email": "harleen.kaur@test.com", "event_title": "AP Dhillon Brownprint Tour"},
    {"user_email": "amritpal.singh@test.com", "event_title": "AP Dhillon Brownprint Tour"},
    {"user_email": "baljit.singh@test.com", "event_title": "AP Dhillon Brownprint Tour"},

    # Earth to Mars
    {"user_email": "parmeet.kaur@test.com", "event_title": "Harkirat Sangha Live - Earth to Mars"},
    {"user_email": "ranjit.singh@test.com", "event_title": "Harkirat Sangha Live - Earth to Mars"},
    {"user_email": "sukhpreet.kaur@test.com", "event_title": "Harkirat Sangha Live - Earth to Mars"},

    # Punjabi Indie Night
    {"user_email": "deepak.singh@test.com", "event_title": "Punjabi Indie Night – Local Legends"},
    {"user_email": "mandeep.kaur@test.com", "event_title": "Punjabi Indie Night – Local Legends"},
]

async def seed_bookings(db: AsyncSession):
    result = await db.execute(select(Booking))
    existing_booking = result.scalars().first()

    if existing_booking is not None:
        return

    for booking in bookings:
        user_result = await db.execute(select(User).where(User.email==booking["user_email"]))
        u = user_result.scalars().one_or_none()

        if u is None:
            continue

        event_result = await db.execute(select(Event).where(Event.title==booking["event_title"]))
        e = event_result.scalars().one_or_none()

        if e is None:
            continue

        if e.available_tickets < 1:
            continue

        b = Booking(user_id=u.id, event_id=e.id)
        e.available_tickets -= 1
        db.add(b)

    await db.commit()