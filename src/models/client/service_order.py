from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coach_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coach_profile_id: Mapped[int] = mapped_column(
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("coach_services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("coach_products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    order_type: Mapped[str] = mapped_column(
        String(50),
        default="service",
        nullable=False,
    )

    booking_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    booking_time: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    referral_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    amount: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    client_fee: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    client_fee_percent: Mapped[str] = mapped_column(
        String(20),
        default="3.00",
        nullable=False,
    )

    total_amount: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    coach_fee: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    coach_fee_percent: Mapped[str] = mapped_column(
        String(20),
        default="5.00",
        nullable=False,
    )

    coach_earning: Mapped[str] = mapped_column(
        String(50),
        default="0.00",
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    payment_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    payment_method: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    transaction_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    is_on_call: Mapped[bool] = mapped_column(
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

    user = relationship("User", foreign_keys=[user_id])
    coach = relationship("User", foreign_keys=[coach_id])
    coach_profile = relationship("CoachProfile", foreign_keys=[coach_profile_id])
    service = relationship("CoachService", foreign_keys=[service_id])
    product = relationship("CoachProduct", foreign_keys=[product_id])
