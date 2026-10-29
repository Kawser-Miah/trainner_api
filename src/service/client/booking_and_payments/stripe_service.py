import uuid
from datetime import datetime, timezone
from decimal import Decimal
import stripe
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_service_order_by_id,
)
from src.schemas.client.booking_and_payments.stripe_schemas import (
    CheckoutSessionData,
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse,
)


async def create_stripe_checkout_session_service(
    payload: CreateCheckoutSessionRequest,
    current_user: User,
    db: Session,
) -> CreateCheckoutSessionResponse:
    order = get_service_order_by_id(db=db, order_id=payload.booking_id)
    if not order:
        raise AppException(
            message="Booking not found.",
            status=404,
            error="BOOKING_NOT_FOUND",
        )

    # 1. Authorization: Only the booking client can initiate checkout
    if order.user_id != current_user.id:
        raise AppException(
            message="You are not authorized to pay for this booking.",
            status=403,
            error="FORBIDDEN",
        )

    # 2. Check already paid
    if order.payment_status in ["paid", "completed"]:
        raise AppException(
            message="This booking has already been paid.",
            status=400,
            error="ALREADY_PAID",
        )

    # 3. Check cancelled / rejected
    if order.status in ["cancelled", "rejected"]:
        raise AppException(
            message="This booking has been cancelled.",
            status=400,
            error="BOOKING_CANCELLED",
        )

    # 4. Check reservation expiry (15m window)
    now = datetime.now(timezone.utc)
    is_expired = False
    if order.status == "expired" or order.payment_status == "expired":
        is_expired = True
    elif order.payment_due_at and order.payment_due_at <= now:
        is_expired = True

    if is_expired:
        order.status = "expired"
        order.payment_status = "expired"
        db.commit()
        raise AppException(
            message="This booking reservation has expired. Please create a new booking.",
            status=400,
            error="BOOKING_EXPIRED",
        )

    # 5. Financial figures
    price = order.amount or "0.00"
    client_fee = order.client_fee or "0.00"
    client_fee_percent = order.client_fee_percent or "3.00"
    total = order.total_amount or "0.00"
    currency = order.currency or "USD"

    credit_used_dec = Decimal("0.00")
    if payload.credit_used:
        try:
            credit_used_dec = Decimal(payload.credit_used)
        except Exception:
            credit_used_dec = Decimal("0.00")

    total_dec = Decimal(total)
    payable_dec = max(Decimal("0.00"), total_dec - credit_used_dec)
    is_free = (payable_dec == Decimal("0.00"))

    credit_used_str = f"{credit_used_dec:.2f}"
    payable_str = f"{payable_dec:.2f}"

    session_id = ""
    checkout_url = ""

    if is_free:
        session_id = f"free_{uuid.uuid4().hex[:12]}"
        checkout_url = ""
    else:
        if settings.stripe_secret_key and settings.stripe_secret_key.strip():
            stripe.api_key = settings.stripe_secret_key.strip()
            unit_amount_cents = int(round(payable_dec * 100))
            service_title = order.service.title if order.service else (order.product.title if order.product else "Coaching Session")
            coach_name = order.coach.full_name if order.coach else "Coach"

            try:
                session = stripe.checkout.Session.create(
                    mode="payment",
                    line_items=[
                        {
                            "price_data": {
                                "currency": currency.lower(),
                                "product_data": {
                                    "name": f"{service_title} with {coach_name}",
                                },
                                "unit_amount": unit_amount_cents,
                            },
                            "quantity": 1,
                        }
                    ],
                    client_reference_id=str(order.id),
                    metadata={
                        "booking_id": str(order.id),
                        "user_id": str(current_user.id),
                        "order_type": order.order_type,
                    },
                    success_url=payload.success_url,
                    cancel_url=payload.cancel_url,
                )
                session_id = session.id
                checkout_url = session.url or ""
            except stripe.error.StripeError as e:
                raise AppException(
                    message=e.user_message or str(e),
                    status=400,
                    error="STRIPE_ERROR",
                )
        else:
            session_id = f"cs_test_{uuid.uuid4().hex[:16]}"
            checkout_url = f"https://checkout.stripe.com/c/pay/{session_id}"

    order.payment_method = "stripe"
    order.transaction_id = session_id
    db.commit()

    return CreateCheckoutSessionResponse(
        success=True,
        status=200,
        message="Checkout session created successfully.",
        data=CheckoutSessionData(
            session_id=session_id,
            checkout_url=checkout_url,
            is_free=is_free,
            booking_id=order.id,
            price=price,
            client_fee=client_fee,
            client_fee_percent=client_fee_percent,
            total=total,
            credit_used=credit_used_str,
            payable=payable_str,
            currency=currency,
        ),
    )
