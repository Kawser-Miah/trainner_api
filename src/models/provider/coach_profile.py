from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class CoachProfile(Base):
    __tablename__ = "coach_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    profile_photo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    headline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    about: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    introduction_video: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    introduction_video_duration: Mapped[int | None] = mapped_column(
        Integer,
        default=0,
        nullable=True,
    )

    video_duration: Mapped[int | None] = mapped_column(
        Integer,
        default=0,
        nullable=True,
    )

    video_display_duration: Mapped[str | None] = mapped_column(
        String(50),
        default="0:00",
        nullable=True,
    )

    introduction_video_thumbnail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    affiliate_commission_percent: Mapped[str] = mapped_column(
        String(20),
        default="20.00",
        nullable=False,
    )

    auto_approve_affiliates: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    expertises: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    languages: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    rejection_reason: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    avg_rating: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    total_reviews: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed_sessions_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    success_rate: Mapped[float | None] = mapped_column(
        Float,
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

    user = relationship(
        "User",
        back_populates="coach_profile",
    )

    categories = relationship(
        "Category",
        secondary="coach_profile_categories",
        back_populates="coach_profiles",
    )

    certifications = relationship(
        "CoachCertification",
        back_populates="coach_profile",
        cascade="all, delete-orphan",
    )

    qualifications = relationship(
        "CoachQualification",
        back_populates="coach_profile",
        cascade="all, delete-orphan",
    )
