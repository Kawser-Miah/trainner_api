from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.client.service_booking import ServiceBooking


class Order(Base):
    __tablename__ = "orders"

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

    order_type: Mapped[str] = mapped_column(
        String(50),
        default="service",
        nullable=False,
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

    service_booking = relationship(
        "ServiceBooking",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )

    product_purchase = relationship(
        "ProductPurchase",
        back_populates="order",
        uselist=False,
    )

    def __init__(self, **kwargs: Any):
        service_id = kwargs.pop("service_id", None)
        booking_date = kwargs.pop("booking_date", None)
        booking_time = kwargs.pop("booking_time", None)
        is_on_call = kwargs.pop("is_on_call", False)
        is_rescheduled = kwargs.pop("is_rescheduled", False)
        payment_due_at = kwargs.pop("payment_due_at", None)
        product_id = kwargs.pop("product_id", None)

        super().__init__(**kwargs)

        order_type_val = kwargs.get("order_type", getattr(self, "order_type", "service"))
        if order_type_val == "service" or service_id or booking_date or booking_time:
            if not self.service_booking:
                self.service_booking = ServiceBooking(
                    service_id=service_id,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    is_on_call=is_on_call,
                    is_rescheduled=is_rescheduled,
                    payment_due_at=payment_due_at,
                )
        if product_id:
            from src.models.client.product_purchase import ProductPurchase
            if not self.product_purchase:
                self.product_purchase = ProductPurchase(
                    user_id=self.user_id,
                    product_id=product_id,
                    price_paid=self.amount,
                )

    @property
    def booking_date(self) -> str | None:
        return self.service_booking.booking_date if self.service_booking else None

    @booking_date.setter
    def booking_date(self, val: str | None):
        if not self.service_booking:
            self.service_booking = ServiceBooking(booking_date=val)
        else:
            self.service_booking.booking_date = val

    @property
    def booking_time(self) -> str | None:
        return self.service_booking.booking_time if self.service_booking else None

    @booking_time.setter
    def booking_time(self, val: str | None):
        if not self.service_booking:
            self.service_booking = ServiceBooking(booking_time=val)
        else:
            self.service_booking.booking_time = val

    @property
    def service_id(self) -> int | None:
        return self.service_booking.service_id if self.service_booking else None

    @service_id.setter
    def service_id(self, val: int | None):
        if not self.service_booking:
            self.service_booking = ServiceBooking(service_id=val)
        else:
            self.service_booking.service_id = val

    @property
    def service(self):
        return self.service_booking.service if self.service_booking else None

    @property
    def is_rescheduled(self) -> bool:
        return self.service_booking.is_rescheduled if self.service_booking else False

    @is_rescheduled.setter
    def is_rescheduled(self, val: bool):
        if not self.service_booking:
            self.service_booking = ServiceBooking(is_rescheduled=val)
        else:
            self.service_booking.is_rescheduled = val

    @property
    def product_id(self) -> int | None:
        return self.product_purchase.product_id if self.product_purchase else None

    @product_id.setter
    def product_id(self, val: int | None):
        if not self.product_purchase:
            from src.models.client.product_purchase import ProductPurchase
            self.product_purchase = ProductPurchase(
                user_id=self.user_id,
                product_id=val,
                price_paid=self.amount,
            )
        else:
            self.product_purchase.product_id = val

    @property
    def product(self):
        return self.product_purchase.product if self.product_purchase else None

    @property
    def is_on_call(self) -> bool:
        return self.service_booking.is_on_call if self.service_booking else False

    @is_on_call.setter
    def is_on_call(self, val: bool):
        if not self.service_booking:
            self.service_booking = ServiceBooking(is_on_call=val)
        else:
            self.service_booking.is_on_call = val

    @property
    def payment_due_at(self) -> datetime | None:
        return self.service_booking.payment_due_at if self.service_booking else None

    @payment_due_at.setter
    def payment_due_at(self, val: datetime | None):
        if not self.service_booking:
            self.service_booking = ServiceBooking(payment_due_at=val)
        else:
            self.service_booking.payment_due_at = val

