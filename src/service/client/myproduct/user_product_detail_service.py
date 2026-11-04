from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.myproduct.user_product_repository import (
    get_user_paid_product_order_by_id,
)
from src.schemas.client.myproduct.user_product_schemas import (
    UserPurchasedProductItem,
)
from src.service.client.myproduct.helpers import (
    build_product_item_from_order,
)


async def get_user_product_detail_service(
    db: Session,
    current_user: User,
    product_order_id: int,
    request: Request | None = None,
) -> UserPurchasedProductItem:
    """Retrieve details for a single paid product order."""
    order = get_user_paid_product_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=product_order_id,
    )
    if not order:
        raise AppException(
            message="Product booking details not found.",
            status=404,
            error="PRODUCT_ORDER_NOT_FOUND",
        )
    return build_product_item_from_order(order=order, request=request)
