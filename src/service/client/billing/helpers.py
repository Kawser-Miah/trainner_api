from datetime import datetime, timezone
from fastapi import Request

from src.models.client.order import Order
from src.schemas.client.billing.user_billing_schemas import (
    UserBillingHistoryItem,
)
from src.utils.media import build_media_url, get_base_url


def _format_iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat()
    return iso.replace("+00:00", "Z") if iso.endswith("+00:00") else iso


def build_billing_item_from_order(
    order: Order,
    request: Request | None = None,
) -> UserBillingHistoryItem:
    coach_profile = order.coach_profile
    coach_user = order.coach or (coach_profile.user if coach_profile else None)
    coach_name = (
        coach_user.full_name
        if coach_user and coach_user.full_name
        else ""
    )

    photo_raw = (
        getattr(coach_profile, "profile_photo", None)
        or (coach_user.photo_url if coach_user else None)
    )
    coach_avatar = (
        build_media_url(photo_raw, request) if photo_raw else None
    )

    if order.order_type == "product":
        title = order.product.title if order.product else "Digital Product"
        booking_date = None
    else:
        title = order.service.title if order.service else "Coaching Session"
        booking_date = order.booking_date

    paid_at_dt = order.paid_at or (
        order.created_at if order.payment_status in ("paid", "refunded") else None
    )
    paid_at_str = _format_iso(paid_at_dt)

    refunded_at_dt = None
    if order.payment_status == "refunded":
        refunded_at_dt = order.refunded_at or order.updated_at
    refunded_at_str = _format_iso(refunded_at_dt)

    base_url = get_base_url(request)
    receipt_url = (
        f"{base_url}/api/v1/user/billing-history/{order.id}/receipt/"
        if base_url
        else f"/api/v1/user/billing-history/{order.id}/receipt/"
    )

    try:
        amount_str = f"{float(order.amount):.2f}"
    except (ValueError, TypeError):
        amount_str = order.amount or "0.00"

    return UserBillingHistoryItem(
        id=order.id,
        type=order.order_type,
        title=title,
        coach_name=coach_name,
        coach_avatar=coach_avatar,
        amount=amount_str,
        currency=order.currency or "USD",
        status=order.payment_status,
        booking_status=order.status,
        booking_date=booking_date,
        paid_at=paid_at_str,
        refunded_at=refunded_at_str,
        receipt_url=receipt_url,
    )

