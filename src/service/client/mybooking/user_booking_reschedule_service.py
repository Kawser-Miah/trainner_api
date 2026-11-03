from datetime import datetime, timezone
from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_coach_orders_for_date,
    get_reviewed_coach_profile_ids,
    get_user_service_order_by_id,
)
from src.schemas.client.booking_and_payments.user_booking_schemas import (
    RescheduleBookingRequest,
    UserBookingItem,
)
from src.service.client.booking_and_payments.availability_validator import (
    check_slot_conflicts,
    parse_time_to_minutes,
    validate_coach_working_hours,
    validate_not_in_past,
)
from src.service.client.mybooking.helpers import (
    CONFIRMED_STATUSES,
    _booking_start,
    _build_booking_item,
)


async def reschedule_user_booking_service(
    db: Session,
    current_user: User,
    booking_id: int,
    payload: RescheduleBookingRequest,
    request: Request | None = None,
) -> UserBookingItem:
    # 1. Fetch the confirmed paid booking
    order = get_user_service_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=booking_id,
        payment_status="paid",
    )
    if not order:
        raise AppException(
            message="Booking not found.",
            status=404,
            error="BOOKING_NOT_FOUND",
        )

    # 2. Check if booking is in confirmed status
    if order.status not in CONFIRMED_STATUSES:
        raise AppException(
            message="Only confirmed bookings can be rescheduled.",
            status=400,
            error="BOOKING_NOT_CONFIRMED",
        )

    # 3. Check if already rescheduled
    if order.is_rescheduled:
        raise AppException(
            message="This booking has already been rescheduled.",
            status=400,
            error="ALREADY_RESCHEDULED",
        )

    # 4. Check if current session has already passed
    now = datetime.now()
    current_start = _booking_start(order)
    if current_start and current_start < now:
        raise AppException(
            message="Cannot reschedule a booking whose session has already passed.",
            status=400,
            error="SESSION_ALREADY_PASSED",
        )

    # 5. Validate new booking date and time
    start_min = parse_time_to_minutes(payload.booking_time)
    validate_not_in_past(
        booking_date_str=payload.booking_date,
        start_min=start_min,
        now=now,
    )

    # 6. Fetch coach profile & service
    coach_profile = order.coach_profile
    service = order.service
    if not coach_profile or not service:
        raise AppException(
            message="Associated coach profile or service not found.",
            status=404,
            error="SERVICE_NOT_FOUND",
        )

    session_duration = service.session_duration if service and service.session_duration else 60
    end_min = start_min + session_duration

    # 7. Validate coach working hours and leave
    validate_coach_working_hours(
        availability=coach_profile.availability,
        booking_date_str=payload.booking_date,
        start_min=start_min,
        end_min=end_min,
    )

    # 8. Check for slot conflicts with other bookings (excluding this order itself)
    existing_orders = get_coach_orders_for_date(
        db=db,
        coach_profile_id=coach_profile.id,
        booking_date=payload.booking_date,
    )
    other_orders = [o for o in existing_orders if o.id != order.id]
    check_slot_conflicts(
        existing_orders=other_orders,
        new_start_min=start_min,
        new_end_min=end_min,
        db=db,
        now=datetime.now(timezone.utc),
    )

    # 9. Format new booking time as HH:MM:SS (24-hour)
    formatted_time = f"{start_min // 60:02d}:{start_min % 60:02d}:00"

    # 10. Update booking
    if not order.service_booking:
        raise AppException(
            message="Service booking record not found.",
            status=404,
            error="BOOKING_NOT_FOUND",
        )

    order.service_booking.booking_date = payload.booking_date
    order.service_booking.booking_time = formatted_time
    order.service_booking.is_rescheduled = True

    db.add(order.service_booking)
    db.commit()
    db.refresh(order)

    # 11. Build and return UserBookingItem
    reviewed = get_reviewed_coach_profile_ids(
        db=db,
        user_id=current_user.id,
        coach_profile_ids=[order.coach_profile_id],
    )
    return _build_booking_item(order, reviewed, datetime.now(), request)

