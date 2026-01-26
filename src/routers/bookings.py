from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.database import get_db
from src.deps.auth import get_current_user
from src.models import User, Event, Booking

booking_router = APIRouter()

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

            # 2️⃣ Check availability AFTER lock
            if event.available_tickets < 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Event is sold out",
                )

            # 3️⃣ Create booking + decrement tickets
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