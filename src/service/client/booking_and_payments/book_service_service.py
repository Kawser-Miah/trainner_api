from datetime import datetime, timedelta, timezone
from fastapi import Request
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.models.client.service_order import ServiceOrder
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    create_service_order,
    get_coach_orders_for_date,
    get_service_for_booking,
)
from src.service.client.booking_and_payments.availability_validator import (
    check_slot_conflicts,
    parse_time_to_minutes,
    validate_coach_working_hours,
    validate_not_in_past,
)
from src.schemas.client.booking_and_payments.booking_schemas import (
    BookServiceRequest,
    OrderCategoryResponse,
    OrderCoachResponse,
    OrderServiceResponse,
    OrderUserResponse,
    ServiceOrderDetailResponse,
)
from src.utils.media import build_media_url


def format_iso_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


async def book_service_service(
    payload: BookServiceRequest,
    current_user: User,
    db: Session,
    request: Request | None = None,
) -> ServiceOrderDetailResponse:
    # 1. Very first check: Ensure requested booking date and time are not in the past
    start_min = parse_time_to_minutes(payload.booking_time)
    validate_not_in_past(
        booking_date_str=payload.booking_date,
        start_min=start_min,
    )

    # 2. Fetch service with category, coach profile and user
    service = get_service_for_booking(db=db, service_id=payload.service_id)
    if not service:
        raise AppException(
            message="Service not found.",
            status=404,
            error="SERVICE_NOT_FOUND",
        )

    # 3. Fetch coach profile & user
    coach_profile = service.coach_profile
    if not coach_profile:
        raise AppException(
            message="Coach profile not found for this service.",
            status=404,
            error="COACH_PROFILE_NOT_FOUND",
        )

    coach_user = coach_profile.user
    if not coach_user:
        raise AppException(
            message="Coach user account not found.",
            status=404,
            error="COACH_NOT_FOUND",
        )

    # 4. Check for self-booking
    if current_user.id == coach_user.id:
        raise AppException(
            message="You cannot book your own service.",
            status=400,
            error="SELF_BOOKING_NOT_ALLOWED",
        )

    # 5. Validate session interval and coach working hours
    session_duration = service.session_duration if service and service.session_duration else 60
    end_min = start_min + session_duration

    validate_coach_working_hours(
        availability=coach_profile.availability,
        booking_date_str=payload.booking_date,
        start_min=start_min,
        end_min=end_min,
    )

    # 6. Check slot conflicts & auto-release expired pending bookings
    now_utc = datetime.now(timezone.utc)
    existing_orders = get_coach_orders_for_date(
        db=db,
        coach_profile_id=coach_profile.id,
        booking_date=payload.booking_date,
    )
    check_slot_conflicts(
        existing_orders=existing_orders,
        new_start_min=start_min,
        new_end_min=end_min,
        db=db,
        now=now_utc,
    )

    # 6. Fee & amount calculations
    try:
        price = float(service.price or "0.00")
    except (ValueError, TypeError):
        price = 0.0

    client_fee_pct = float(settings.client_fee_percentage)
    coach_fee_pct = float(settings.coach_fee_percentage)

    client_fee_val = round(price * (client_fee_pct / 100.0), 2)
    total_amount_val = round(price + client_fee_val, 2)

    coach_fee_val = round(price * (coach_fee_pct / 100.0), 2)
    coach_earning_val = round(price - coach_fee_val, 2)

    client_fee_percent = f"{client_fee_pct:.2f}"
    coach_fee_percent = f"{coach_fee_pct:.2f}"

    amount_str = f"{price:.2f}"
    client_fee_str = f"{client_fee_val:.2f}"
    total_amount_str = f"{total_amount_val:.2f}"
    coach_fee_str = f"{coach_fee_val:.2f}"
    coach_earning_str = f"{coach_earning_val:.2f}"
    currency_str = service.currency or "USD"

    # Set temporary slot lock / payment grace period
    payment_due_at = now_utc + timedelta(minutes=settings.booking_payment_timeout_minutes)

    # 7. Persist order
    new_order = ServiceOrder(
        user_id=current_user.id,
        coach_id=coach_user.id,
        coach_profile_id=coach_profile.id,
        service_id=service.id,
        product_id=None,
        order_type="service",
        booking_date=payload.booking_date,
        booking_time=payload.booking_time,
        referral_code=payload.referral_code or "",
        amount=amount_str,
        client_fee=client_fee_str,
        client_fee_percent=client_fee_percent,
        total_amount=total_amount_str,
        coach_fee=coach_fee_str,
        coach_fee_percent=coach_fee_percent,
        coach_earning=coach_earning_str,
        currency=currency_str,
        status="pending",
        payment_status="pending",
        payment_method=None,
        transaction_id=None,
        is_on_call=False,
        payment_due_at=payment_due_at,
    )
    created_order = create_service_order(db=db, order=new_order)

    # 6. Build response
    coach_photo = build_media_url(
        coach_user.photo_url or getattr(coach_profile, "profile_photo", None),
        request,
    )

    category_data = OrderCategoryResponse(
        id=service.category.id if service.category else 0,
        name=service.category.name if service.category else "",
        description=service.category.description or "" if service.category else "",
    )

    service_data = OrderServiceResponse(
        id=service.id,
        title=service.title,
        description=service.description or "",
        service_type=service.service_type,
        session_format=service.session_format,
        session_duration=service.session_duration,
        price=amount_str,
        currency=currency_str,
        booking_type=service.booking_type,
        session_url=service.session_url,
        category=category_data,
    )

    user_data = OrderUserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_number=current_user.phone or "",
    )

    coach_data = OrderCoachResponse(
        id=coach_user.id,
        full_name=coach_user.full_name,
        email=coach_user.email,
        phone_number=coach_user.phone or "",
        profile_photo=coach_photo,
        about=coach_profile.about or "",
    )

    return ServiceOrderDetailResponse(
        id=created_order.id,
        user=user_data,
        coach=coach_data,
        service=service_data,
        product=None,
        order_type=created_order.order_type,
        booking_date=created_order.booking_date,
        booking_time=created_order.booking_time,
        amount=created_order.amount,
        client_fee=created_order.client_fee,
        client_fee_percent=created_order.client_fee_percent,
        total_amount=created_order.total_amount,
        coach_fee=created_order.coach_fee,
        coach_fee_percent=created_order.coach_fee_percent,
        coach_earning=created_order.coach_earning,
        currency=created_order.currency,
        status=created_order.status,
        payment_status=created_order.payment_status,
        payment_method=created_order.payment_method,
        transaction_id=created_order.transaction_id,
        is_on_call=created_order.is_on_call,
        payment_due_at=format_iso_datetime(created_order.payment_due_at) if created_order.payment_due_at else None,
        created_at=format_iso_datetime(created_order.created_at),
        updated_at=format_iso_datetime(created_order.updated_at),
    )
