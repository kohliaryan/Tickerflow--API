from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.database import get_db
from src.deps.auth import get_current_user
from src.models import User, Event, Booking

booking_router = APIRouter(prefix="bookings")

@booking_router.post("/{event_id}/book", status_code=status.HTTP_201_CREATED)
async def book_ticket(
    event_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
            stmt = (
                select(Event)
                .where(
                    Event.id == event_id,
                    Event.is_active.is_(True),
                )
                .with_for_update()
            )

            result = await db.execute(stmt)
            event = result.scalars().one_or_none()

            if event is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid or inactive event",
                )

            if event.available_tickets < 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Event is sold out",
                )

            event.available_tickets -= 1
            booking = Booking(
                user_id=user.id,
                event_id=event.id,
            )

            db.add(booking)

    except IntegrityError:
        # UNIQUE (user_id, event_id) violated
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already booked this event",
        )

    return {"msg": "Booked successfully"}

@booking_router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_booking(
        booking_id: int,
        user: User=Depends(get_current_user),
        db: AsyncSession=Depends(get_db)
):
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )

    booking = result.scalars().one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No booking found!"
        )

    if booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Permitted!"
        )

    result_event = await db.execute(
        select(Event).where(Event.id==booking.event_id)
    )
    event = result_event.scalars().one_or_none()

    now = datetime.now(timezone.utc)

    if event.event_date <= now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Event already started or finished",
        )

    cancellation_deadline = event.event_date - timedelta(hours=24)

    if now >= cancellation_deadline:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tickets cannot be cancelled within 24 hours of the event",
        )

    event.available_tickets += 1

    await db.delete(booking)
    await db.commit()

    return
