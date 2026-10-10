from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class CoachAvailability(Base):
    __tablename__ = "coach_availabilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    coach_profile_id: Mapped[int] = mapped_column(
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    weekly: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    on_call: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    on_call_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    time_off: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
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
        back_populates="availability",
    )
