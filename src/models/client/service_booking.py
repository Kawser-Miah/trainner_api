from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ServiceBooking(Base):
    __tablename__ = "service_bookings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("coach_services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    booking_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    booking_time: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_on_call: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_rescheduled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    payment_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order = relationship("Order", back_populates="service_booking")
    service = relationship("CoachService")

