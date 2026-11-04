from datetime import datetime
from fastapi import Request

from src.models.client.order import Order
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


def build_product_item_from_order(
    order: Order,
    request: Request | None = None,
) -> UserPurchasedProductItem:
    product = order.product
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

    return UserPurchasedProductItem(
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
