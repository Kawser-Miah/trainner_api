from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.myproduct.user_product_repository import (
    get_user_paid_product_orders,
)
from src.schemas.client.myproduct.user_product_schemas import (
    UserPurchasedProductItem,
)
from src.service.client.myproduct.helpers import (
    build_product_item_from_order,
)


async def get_user_purchased_products_service(
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> list[UserPurchasedProductItem]:
    """Retrieve all paid product orders for the authenticated client."""
    orders = get_user_paid_product_orders(db=db, user_id=current_user.id)
    return [
        build_product_item_from_order(order=order, request=request)
        for order in orders
    ]
