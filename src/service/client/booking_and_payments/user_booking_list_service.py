from datetime import datetime

from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.models.client.service_order import ServiceOrder
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_reviewed_coach_profile_ids,
    get_user_service_orders,
)
from src.schemas.client.booking_and_payments.user_booking_schemas import UserBookingItem
from src.service.client.booking_and_payments.availability_validator import parse_time_to_minutes
from src.utils.media import build_media_url

VALID_STATUS_FILTERS = {"upcoming", "pending", "confirmed", "completed", "cancelled", "rejected"}
# "upcoming" = still-active bookings whose session has not started yet.
UPCOMING_STATUSES = {"pending", "confirmed"}


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


def _matches(order: ServiceOrder, filters: set[str], now: datetime) -> bool:
    if not filters:
        return True
    if order.status in filters:
        return True
    if "upcoming" in filters and order.status in UPCOMING_STATUSES:
        start = _booking_start(order)
        return start is not None and start >= now
    return False


async def get_user_booking_list_service(
    db: Session,
    current_user: User,
    status: str | None = None,
    request: Request | None = None,
) -> list[UserBookingItem]:
    filters = parse_status_filter(status)
    db_statuses = None
    if filters:
        db_statuses = list((filters - {"upcoming"}) | (UPCOMING_STATUSES if "upcoming" in filters else set()))

    orders = get_user_service_orders(db=db, user_id=current_user.id, statuses=db_statuses)
    now = datetime.now()
    orders = [order for order in orders if _matches(order, filters, now)]

    reviewed = get_reviewed_coach_profile_ids(
        db=db,
        user_id=current_user.id,
        coach_profile_ids=list({order.coach_profile_id for order in orders}),
    )

    items: list[UserBookingItem] = []
    for order in orders:
        service = order.service
        coach = order.coach
        coach_profile = order.coach_profile
        start = _booking_start(order)
        is_active = order.status in UPCOMING_STATUSES and (start is None or start >= now)
        items.append(
            UserBookingItem(
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
                can_join=order.status == "confirmed" and order.payment_status == "paid",
                preparation_instructions=(service.preparation_instructions or "") if service else "",
                booking_date=order.booking_date,
                booking_time=_format_time(order),
                amount=order.amount,
                currency=order.currency,
                cancellation_policy=(service.cancellation_policy or "") if service else "",
                status=order.status,
                payment_status=order.payment_status,
                payment_method=order.payment_method,
                # notes / coach_message / reschedules are not stored on service_orders
                # (columns were dropped in c35ae272d2f9), so defaults are returned.
                is_rescheduled=False,
                notes=None,
                coach_message="",
                has_reviewed=order.coach_profile_id in reviewed,
                can_cancel=is_active,
                can_reschedule=is_active and order.status == "confirmed",
            )
        )
    return items
