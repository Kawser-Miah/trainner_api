from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.models.client.service_order import ServiceOrder
from src.repository.client.booking_and_payments.booking_and_payments_repository import (
    create_service_order,
    get_product_for_purchase,
)
from src.repository.client.browse.client_browse_repository import (
    is_product_purchased_by_user,
)
from src.schemas.client.booking_and_payments.booking_schemas import (
    OrderCoachResponse,
    OrderUserResponse,
)
from src.schemas.client.booking_and_payments.product_purchase_schemas import (
    OrderProductDetail,
    ProductPurchaseResponseData,
    PurchaseProductRequest,
)
from src.utils.media import build_media_url


def format_iso_datetime(dt: datetime | None) -> str | None:
    if not dt:
        return None
    return dt.isoformat()


async def purchase_product_service(
    payload: PurchaseProductRequest,
    current_user: User,
    db: Session,
    request: Request | None = None,
) -> ProductPurchaseResponseData:
    product = get_product_for_purchase(db=db, product_id=payload.product_id)
    if not product:
        raise AppException(
            message="Product not found.",
            status=404,
            error="PRODUCT_NOT_FOUND",
        )

    coach_profile = product.coach_profile
    if not coach_profile:
        raise AppException(
            message="Coach profile not found for this product.",
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

    # 1. Self-purchase validation
    if current_user.id == coach_user.id:
        raise AppException(
            message="You cannot purchase your own product.",
            status=400,
            error="SELF_PURCHASE_NOT_ALLOWED",
        )

    # 2. Check if already purchased
    if is_product_purchased_by_user(db=db, user_id=current_user.id, product=product):
        raise AppException(
            message="You have already purchased this product.",
            status=400,
            error="ALREADY_PURCHASED",
        )

    # 3. Product availability check
    if product.status != "published":
        raise AppException(
            message="This product is not currently available for purchase.",
            status=400,
            error="PRODUCT_UNAVAILABLE",
        )

    # 4. Fee & amount calculations
    try:
        price = float(product.price or "0.00")
    except (ValueError, TypeError):
        price = 0.0

    client_fee_pct = 0.00
    coach_fee_pct = float(settings.coach_fee_percentage)

    client_fee_val = 0.00
    total_amount_val = price

    coach_fee_val = round(price * (coach_fee_pct / 100.0), 2)
    coach_earning_val = round(price - coach_fee_val, 2)

    amount_str = f"{price:.2f}"
    client_fee_str = f"{client_fee_val:.2f}"
    client_fee_percent = f"{client_fee_pct:.2f}"
    total_amount_str = f"{total_amount_val:.2f}"
    coach_fee_str = f"{coach_fee_val:.2f}"
    coach_fee_percent = f"{coach_fee_pct:.2f}"
    coach_earning_str = f"{coach_earning_val:.2f}"
    currency_str = getattr(product, "currency", "USD") or "USD"

    # 5. Persist order
    new_order = ServiceOrder(
        user_id=current_user.id,
        coach_id=coach_user.id,
        coach_profile_id=coach_profile.id,
        service_id=None,
        product_id=product.id,
        order_type="product",
        booking_date=None,
        booking_time=None,
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
        payment_due_at=None,
    )
    created_order = create_service_order(db=db, order=new_order)

    # 6. Build response
    coach_photo = build_media_url(
        coach_user.photo_url or getattr(coach_profile, "profile_photo", None),
        request,
    )
    thumbnail_url = build_media_url(product.thumbnail, request) if product.thumbnail else None

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

    product_data = OrderProductDetail(
        id=product.id,
        title=product.title,
        description=product.description or "",
        price=amount_str,
        Thumbnail=thumbnail_url,
    )

    return ProductPurchaseResponseData(
        id=created_order.id,
        user=user_data,
        coach=coach_data,
        service=None,
        product=product_data,
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
        notes=None,
        can_join=False,
        coach_message="",
        is_on_call=created_order.is_on_call,
        payment_due_at=None,
        created_at=format_iso_datetime(created_order.created_at) or "",
        updated_at=format_iso_datetime(created_order.updated_at) or "",
    )

