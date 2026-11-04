from sqlalchemy.orm import Session, joinedload

from src.models.client.order import Order
from src.models.client.product_purchase import ProductPurchase
from src.models.provider.coach_profile.coach_profile import CoachProfile
from src.models.provider.product.coach_product import CoachProduct


def get_user_paid_product_orders(
    db: Session,
    user_id: int,
) -> list[Order]:
    """Retrieve all paid product orders for the client."""
    return (
        db.query(Order)
        .options(
            joinedload(Order.coach),
            joinedload(Order.coach_profile).joinedload(CoachProfile.user),
            joinedload(Order.product_purchase)
            .joinedload(ProductPurchase.product)
            .joinedload(CoachProduct.category),
        )
        .filter(
            Order.user_id == user_id,
            Order.order_type == "product",
            Order.payment_status == "paid",
        )
        .order_by(Order.created_at.desc())
        .all()
    )


def get_user_paid_product_order_by_id(
    db: Session,
    user_id: int,
    order_id: int,
) -> Order | None:
    """Retrieve a single paid product order by ID for the client."""
    return (
        db.query(Order)
        .options(
            joinedload(Order.coach),
            joinedload(Order.coach_profile).joinedload(CoachProfile.user),
            joinedload(Order.product_purchase)
            .joinedload(ProductPurchase.product)
            .joinedload(CoachProduct.category),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.order_type == "product",
            Order.payment_status == "paid",
        )
        .first()
    )
