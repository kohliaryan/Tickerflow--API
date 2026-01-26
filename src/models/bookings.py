from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_booking"),
    )

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
