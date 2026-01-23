from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"), nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="bookings"
    )

    event: Mapped["Event"] = relationship(
        back_populates="bookings"
    )
