from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.myproduct.user_product_repository import (
    get_user_paid_product_orders,
    get_user_standalone_product_purchases,
)
from src.schemas.client.myproduct.user_product_schemas import (
    UserPurchasedProductItem,
)
from src.utils.media import build_media_url


def _format_iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.astimezone()
    else:
        dt = dt.astimezone()
    return dt.isoformat()


async def get_user_purchased_products_service(
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> list[UserPurchasedProductItem]:
    """Retrieve all purchased digital products for the authenticated client."""
    orders = get_user_paid_product_orders(db=db, user_id=current_user.id)
    standalone_purchases = get_user_standalone_product_purchases(
        db=db, user_id=current_user.id
    )

    items: list[UserPurchasedProductItem] = []
    seen_product_ids: set[int] = set()

    for order in orders:
        product = order.product
        if product:
            seen_product_ids.add(product.id)

        coach_profile = order.coach_profile
        coach_user = order.coach or (
            coach_profile.user if coach_profile else None
        )
        coach_name = (
            coach_user.full_name
            if coach_user and coach_user.full_name
            else ""
        )

        photo_raw = (
            getattr(coach_profile, "profile_photo", None)
            or (coach_user.photo_url if coach_user else None)
        )
        coach_profile_photo = (
            build_media_url(photo_raw, request) if photo_raw else None
        )

        title = product.title if product else ""
        category = (
            product.category.name if product and product.category else ""
        )
        price = (
            order.amount
            if order.amount
            else (product.price if product and product.price else "0.00")
        )
        payment_status = order.payment_status or "paid"
        thumbnail_url = (
            build_media_url(product.thumbnail, request)
            if product and product.thumbnail
            else None
        )

        if product and request:
            book_file_url = f"{str(request.base_url).rstrip('/')}/api/v1/user/digital-product-download/{product.id}/"
        elif product:
            book_file_url = f"/api/v1/user/digital-product-download/{product.id}/"
        else:
            book_file_url = None

        items.append(
            UserPurchasedProductItem(
                id=order.id,
                coach_name=coach_name,
                product_title=title,
                product_category=category,
                product_price=price,
                payment_status=payment_status,
                coach_profile_photo=coach_profile_photo,
                created_at=_format_iso(order.created_at),
                Thumbnail=thumbnail_url,
                book_file=book_file_url,
            )
        )

    for purchase in standalone_purchases:
        product = purchase.product
        if not product or product.id in seen_product_ids:
            continue
        seen_product_ids.add(product.id)

        coach_profile = product.coach_profile
        coach_user = coach_profile.user if coach_profile else None
        coach_name = (
            coach_user.full_name
            if coach_user and coach_user.full_name
            else ""
        )

        photo_raw = (
            getattr(coach_profile, "profile_photo", None)
            or (coach_user.photo_url if coach_user else None)
        )
        coach_profile_photo = (
            build_media_url(photo_raw, request) if photo_raw else None
        )

        thumbnail_url = (
            build_media_url(product.thumbnail, request)
            if product.thumbnail
            else None
        )

        if request:
            book_file_url = f"{str(request.base_url).rstrip('/')}/api/v1/user/digital-product-download/{product.id}/"
        else:
            book_file_url = f"/api/v1/user/digital-product-download/{product.id}/"

        items.append(
            UserPurchasedProductItem(
                id=purchase.id,
                coach_name=coach_name,
                product_title=product.title or "",
                product_category=(
                    product.category.name if product.category else ""
                ),
                product_price=str(
                    purchase.price_paid or product.price or "0.00"
                ),
                payment_status="paid",
                coach_profile_photo=coach_profile_photo,
                created_at=_format_iso(purchase.created_at),
                Thumbnail=thumbnail_url,
                book_file=book_file_url,
            )
        )

    return items
