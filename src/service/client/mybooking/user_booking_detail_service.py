from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    get_reviewed_coach_profile_ids,
    get_user_service_order_by_id,
)
from src.schemas.client.booking_and_payments.user_booking_schemas import UserBookingItem
from src.service.client.mybooking.helpers import _build_booking_item


async def get_user_booking_detail_service(
    db: Session,
    current_user: User,
    booking_id: int,
    request: Request | None = None,
) -> UserBookingItem:
    order = get_user_service_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=booking_id,
        payment_status=["paid", "refunded"],
    )
    if not order:
        raise AppException(
            message="Booking not found.",
            status=404,
            error="BOOKING_NOT_FOUND",
        )
    reviewed = get_reviewed_coach_profile_ids(
        db=db,
        user_id=current_user.id,
        coach_profile_ids=[order.coach_profile_id],
    )
    return _build_booking_item(order, reviewed, datetime.now(), request)

