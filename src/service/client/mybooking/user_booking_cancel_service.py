from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session
import stripe

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.mybooking import (
    get_reviewed_coach_profile_ids,
    get_user_service_order_by_id,
    mark_order_cancelled_and_refunded,
)
from src.schemas.client.booking_and_payments.user_booking_schemas import UserBookingItem
from src.service.client.mybooking.helpers import (
    CONFIRMED_STATUSES,
    _booking_start,
    _build_booking_item,
)


async def cancel_user_booking_service(
    db: Session,
    current_user: User,
    booking_id: int,
    request: Request | None = None,
) -> UserBookingItem:
    # 1. Fetch order for the current client
    order = get_user_service_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=booking_id,
        payment_status=None,  # retrieve regardless of payment status for precise validation
    )
    if not order:
        raise AppException(
            message="Booking not found.",
            status=404,
            error="BOOKING_NOT_FOUND",
        )

    # 2. Check if already cancelled
    if order.status == "cancelled" or order.payment_status == "refunded":
        raise AppException(
            message="This booking has already been cancelled.",
            status=400,
            error="ALREADY_CANCELLED",
        )

    # 3. Check if paid
    if order.payment_status != "paid":
        raise AppException(
            message="Only paid bookings can be cancelled and refunded.",
            status=400,
            error="BOOKING_NOT_PAID",
        )

    # 4. Check if confirmed
    if order.status not in CONFIRMED_STATUSES:
        raise AppException(
            message="Only confirmed bookings can be cancelled.",
            status=400,
            error="BOOKING_NOT_CONFIRMED",
        )

    # 5. Check if session has already passed
    now = datetime.now()
    start = _booking_start(order)
    if start and start < now:
        raise AppException(
            message="Cannot cancel a booking whose session has already passed.",
            status=400,
            error="SESSION_ALREADY_PASSED",
        )

    # 6. Execute instant refund via Stripe if configured
    if settings.stripe_secret_key and settings.stripe_secret_key.strip():
        stripe.api_key = settings.stripe_secret_key.strip()
        trx_id = order.transaction_id
        if trx_id and not trx_id.startswith("free_"):
            is_mock = "mock" in trx_id.lower() or trx_id.startswith("mock_")
            if not is_mock:
                refund = None
                try:
                    if trx_id.startswith("pi_"):
                        refund = stripe.Refund.create(payment_intent=trx_id)
                    elif trx_id.startswith("ch_"):
                        refund = stripe.Refund.create(charge=trx_id)
                    elif trx_id.startswith("cs_"):
                        session = stripe.checkout.Session.retrieve(trx_id)
                        pi_id = getattr(session, "payment_intent", None)
                        if isinstance(pi_id, dict):
                            pi_id = pi_id.get("id")
                        if pi_id:
                            refund = stripe.Refund.create(payment_intent=str(pi_id))
                        else:
                            raise AppException(
                                message="Cannot process refund: No payment intent found for this session.",
                                status=400,
                                error="PAYMENT_INTENT_NOT_FOUND",
                            )
                except stripe.error.StripeError as e:
                    raise AppException(
                        message=f"Stripe refund failed: {e.user_message or str(e)}",
                        status=400,
                        error="STRIPE_REFUND_ERROR",
                    )

                refund_status = getattr(refund, "status", None) if refund else None
                if refund_status not in ("succeeded", "pending"):
                    raise AppException(
                        message=f"Stripe refund could not be confirmed (status: {refund_status}).",
                        status=400,
                        error="STRIPE_REFUND_NOT_CONFIRMED",
                    )

    # 7. Update status to cancelled and payment_status to refunded
    order = mark_order_cancelled_and_refunded(db=db, order=order)

    # 8. Return updated booking item
    reviewed = get_reviewed_coach_profile_ids(
        db=db,
        user_id=current_user.id,
        coach_profile_ids=[order.coach_profile_id],
    )
    return _build_booking_item(order, reviewed, datetime.now(), request)

