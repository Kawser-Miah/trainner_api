from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_reviewed_coach_profile_ids,
    get_user_service_orders,
)
from src.schemas.client.booking_and_payments.user_booking_schemas import UserBookingItem
from src.service.client.mybooking.helpers import (
    _build_booking_item,
    _matches,
    parse_status_filter,
)


async def get_user_booking_list_service(
    db: Session,
    current_user: User,
    status: str | None = None,
    request: Request | None = None,
) -> list[UserBookingItem]:
    filters = parse_status_filter(status)
    db_statuses = None
    if filters:
        db_statuses_set = set()
        for f in filters:
            if f in {"upcoming", "confirmed"}:
                db_statuses_set.add("confirmed")
                db_statuses_set.add("upcoming")
            else:
                db_statuses_set.add(f)
        db_statuses = list(db_statuses_set)

    orders = get_user_service_orders(
        db=db,
        user_id=current_user.id,
        statuses=db_statuses,
        payment_status="paid",
    )
    now = datetime.now()
    orders = [order for order in orders if _matches(order, filters)]

    reviewed = get_reviewed_coach_profile_ids(
        db=db,
        user_id=current_user.id,
        coach_profile_ids=list({order.coach_profile_id for order in orders}),
    )

    return [_build_booking_item(order, reviewed, now, request) for order in orders]

