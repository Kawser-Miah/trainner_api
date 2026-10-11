from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class CoachService(Base):
    __tablename__ = "coach_services"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    coach_profile_id: Mapped[int] = mapped_column(
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    service_type: Mapped[str] = mapped_column(
        String(50),
        default="one_time",
        nullable=False,
    )

    session_format: Mapped[str] = mapped_column(
        String(50),
        default="video",
        nullable=False,
    )

    session_duration: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False,
    )

    price: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    booking_type: Mapped[str] = mapped_column(
        String(50),
        default="instant",
        nullable=False,
    )

    who_is_this_service_for: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preparation_instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cancellation_policy: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False,
    )

    session_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="published",
        nullable=False,
    )

    bookings_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    revenue: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
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

    coach_profile = relationship(
        "CoachProfile",
        back_populates="services",
    )

    category = relationship(
        "Category",
    )

    benefits = relationship(
        "CoachServiceBenefit",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="CoachServiceBenefit.id",
    )

    @property
    def coach(self) -> int:
        return self.coach_profile_id


class CoachServiceBenefit(Base):
    __tablename__ = "coach_service_benefits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("coach_services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    outcome: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    service = relationship(
        "CoachService",
        back_populates="benefits",
    )
