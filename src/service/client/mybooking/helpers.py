from datetime import datetime
from fastapi import Request

from src.core.exceptions import AppException
from src.models.client.service_order import ServiceOrder
from src.schemas.client.booking_and_payments.user_booking_schemas import UserBookingItem
from src.service.client.booking_and_payments.availability_validator import parse_time_to_minutes
from src.utils.media import build_media_url

VALID_STATUS_FILTERS = {"upcoming", "pending", "confirmed", "completed", "cancelled", "rejected"}
CONFIRMED_STATUSES = {"confirmed", "upcoming"}


def parse_status_filter(status: str | None) -> set[str]:
    if not status:
        return set()
    requested = {part.strip().lower() for part in status.split(",") if part.strip()}
    invalid = requested - VALID_STATUS_FILTERS
    if invalid:
        raise AppException(
            message=f"Invalid status filter: {', '.join(sorted(invalid))}.",
            status=400,
            error="INVALID_STATUS_FILTER",
        )
    return requested


def _booking_start(order: ServiceOrder) -> datetime | None:
    if not order.booking_date or not order.booking_time:
        return None
    try:
        day = datetime.strptime(order.booking_date, "%Y-%m-%d")
        minutes = parse_time_to_minutes(order.booking_time)
    except (ValueError, AppException):
        return None
    return day.replace(hour=minutes // 60, minute=minutes % 60)


def _format_time(order: ServiceOrder) -> str | None:
    start = _booking_start(order)
    return start.strftime("%H:%M:%S") if start else order.booking_time


def _matches(order: ServiceOrder, filters: set[str]) -> bool:
    if order.payment_status not in {"paid", "refunded"}:
        return False
    if not filters:
        return True
    if order.status in filters:
        return True
    if ("upcoming" in filters or "confirmed" in filters) and order.status in CONFIRMED_STATUSES:
        return True
    return False


def _build_booking_item(
    order: ServiceOrder,
    reviewed: set[int],
    now: datetime,
    request: Request | None,
) -> UserBookingItem:
    service = order.service
    coach = order.coach
    coach_profile = order.coach_profile
    start = _booking_start(order)
    is_rescheduled = bool(getattr(order, "is_rescheduled", False))
    is_active = order.status in CONFIRMED_STATUSES and order.payment_status == "paid" and (start is None or start >= now)
    return UserBookingItem(
        id=order.id,
        provider_user_id=order.coach_id,
        coach_profile_id=order.coach_profile_id,
        coach_name=coach.full_name if coach else "",
        coach_profile_photo=build_media_url(
            (coach.photo_url if coach else None) or getattr(coach_profile, "profile_photo", None),
            request,
        ),
        service_id=order.service_id,
        service_title=service.title if service else "",
        service_category=service.category.name if service and service.category else "",
        service_type=service.service_type if service else "one_time",
        session_format=service.session_format if service else "video",
        session_duration=service.session_duration if service else 60,
        can_join=order.status in CONFIRMED_STATUSES and order.payment_status == "paid",
        preparation_instructions=(service.preparation_instructions or "") if service else "",
        booking_date=order.booking_date,
        booking_time=_format_time(order),
        amount=order.amount,
        currency=order.currency,
        cancellation_policy=(service.cancellation_policy or "") if service else "",
        status=order.status,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        is_rescheduled=is_rescheduled,
        notes=None,
        coach_message="",
        has_reviewed=order.coach_profile_id in reviewed,
        can_cancel=is_active,
        can_reschedule=is_active and not is_rescheduled,
    )

