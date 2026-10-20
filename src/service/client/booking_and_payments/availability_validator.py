from datetime import date, datetime, timedelta, timezone
import re
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.client.service_order import ServiceOrder
from src.models.provider.coach_profile import CoachAvailability


def parse_time_to_minutes(time_str: str) -> int:
    """Parse a 12-hour (e.g. '02:00 PM', '2:00 PM') or 24-hour ('14:00') time string

    into minutes from midnight (0..1439).
    """
    cleaned = (time_str or "").strip().upper()
    if not cleaned:
        raise AppException(
            message="Booking time is required.",
            status=400,
            error="INVALID_TIME_FORMAT",
        )

    # 1. Check for 12-hour AM/PM format (e.g., '02:00 PM', '2:00 PM', '11:30 AM')
    match_12 = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", cleaned)
    if match_12:
        hour, minute, am_pm = match_12.groups()
        h, m = int(hour), int(minute)
        if not (1 <= h <= 12 and 0 <= m < 60):
            raise AppException(
                message="Invalid time values in booking time.",
                status=400,
                error="INVALID_TIME_FORMAT",
            )
        if am_pm == "AM":
            h = 0 if h == 12 else h
        else:  # PM
            h = 12 if h == 12 else h + 12
        return h * 60 + m

    # 2. Check for 24-hour format (e.g., '14:00', '09:30')
    match_24 = re.match(r"^(\d{1,2}):(\d{2})$", cleaned)
    if match_24:
        hour, minute = match_24.groups()
        h, m = int(hour), int(minute)
        if not (0 <= h < 24 and 0 <= m < 60):
            raise AppException(
                message="Invalid time values in booking time.",
                status=400,
                error="INVALID_TIME_FORMAT",
            )
        return h * 60 + m

    raise AppException(
        message=f"Invalid booking time format '{time_str}'. Expected 'HH:MM AM/PM' (e.g. '02:00 PM') or 'HH:MM'.",
        status=400,
        error="INVALID_TIME_FORMAT",
    )


def validate_not_in_past(
    booking_date_str: str,
    start_min: int,
    now: datetime | None = None,
) -> None:
    """Ensure the booking date and time are not in the past.

    If booking is today, ensures requested time is strictly in the future.
    """
    try:
        parsed_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise AppException(
            message="Invalid booking date format. Use 'YYYY-MM-DD' (e.g. '2026-10-13').",
            status=400,
            error="INVALID_DATE_FORMAT",
        )

    current_dt = now or datetime.now()
    today = current_dt.date()

    if parsed_date < today:
        raise AppException(
            message="Cannot book a session in the past.",
            status=400,
            error="PAST_BOOKING_TIME",
        )

    if parsed_date == today:
        current_min = current_dt.hour * 60 + current_dt.minute
        if start_min <= current_min:
            raise AppException(
                message="Cannot book a session in the past. The requested time has already passed today.",
                status=400,
                error="PAST_BOOKING_TIME",
            )


def validate_coach_working_hours(
    availability: CoachAvailability | None,
    booking_date_str: str,
    start_min: int,
    end_min: int,
) -> None:
    """Ensure session fits within the coach's scheduled working hours for the given date,

    and verify the coach is not on leave.
    """
    try:
        parsed_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise AppException(
            message="Invalid booking date format. Use 'YYYY-MM-DD' (e.g. '2026-10-13').",
            status=400,
            error="INVALID_DATE_FORMAT",
        )

    # 1. Check time-off
    time_off = availability.time_off if availability and availability.time_off else []
    time_off_dates = {
        t.get("date") for t in time_off if isinstance(t, dict) and t.get("date")
    }
    if booking_date_str in time_off_dates:
        raise AppException(
            message="The coach is taking time off and unavailable on this date.",
            status=400,
            error="COACH_ON_LEAVE",
        )

    # 2. Get weekly schedule (fallback to Monday-Friday 09:00 - 17:00 if unconfigured)
    weekly = availability.weekly if availability and availability.weekly else []
    if not weekly:
        weekly = [
            {"weekday": i, "start_time": "09:00", "end_time": "17:00"}
            for i in range(5)
        ]

    weekday_num = parsed_date.weekday()  # 0=Monday, ..., 6=Sunday
    day_schedule = next((w for w in weekly if w.get("weekday") == weekday_num), None)

    if not day_schedule:
        raise AppException(
            message="The coach does not have working hours scheduled on this day.",
            status=400,
            error="COACH_NOT_WORKING_ON_DAY",
        )

    day_start_min = parse_time_to_minutes(day_schedule.get("start_time", "09:00"))
    day_end_min = parse_time_to_minutes(day_schedule.get("end_time", "17:00"))

    if start_min < day_start_min or end_min > day_end_min:
        start_str = day_schedule.get("start_time", "09:00")
        end_str = day_schedule.get("end_time", "17:00")
        raise AppException(
            message=f"The requested session time falls outside the coach's working hours ({start_str} - {end_str}).",
            status=400,
            error="OUTSIDE_WORKING_HOURS",
        )


def check_slot_conflicts(
    existing_orders: list[ServiceOrder],
    new_start_min: int,
    new_end_min: int,
    db: Session,
    now: datetime,
) -> None:
    """Check for interval overlaps with existing bookings.

    Releases and updates expired pending bookings automatically.
    """
    has_expired_updates = False

    for order in existing_orders:
        # Check if pending order has timed out on payment
        is_pending_expired = False
        if order.payment_status == "pending":
            if order.payment_due_at is not None:
                is_pending_expired = order.payment_due_at <= now
            elif order.created_at is not None:
                timeout_dt = order.created_at + timedelta(
                    minutes=settings.booking_payment_timeout_minutes
                )
                is_pending_expired = timeout_dt <= now

        if is_pending_expired:
            order.status = "expired"
            order.payment_status = "expired"
            db.add(order)
            has_expired_updates = True
            continue

        # Skip inactive orders
        if order.status in ["cancelled", "rejected", "expired"]:
            continue

        # Calculate existing booking interval
        try:
            ex_start_min = parse_time_to_minutes(order.booking_time or "")
        except AppException:
            continue

        ex_duration = 60
        if order.service and order.service.session_duration:
            ex_duration = order.service.session_duration
        ex_end_min = ex_start_min + ex_duration

        # Interval overlap test: new_start < ex_end AND new_end > ex_start
        if new_start_min < ex_end_min and new_end_min > ex_start_min:
            if has_expired_updates:
                db.commit()
            raise AppException(
                message="This time slot overlaps with an existing booking.",
                status=409,
                error="SLOT_ALREADY_BOOKED",
            )

    if has_expired_updates:
        db.commit()
