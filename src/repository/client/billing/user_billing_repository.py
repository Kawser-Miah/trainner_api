from sqlalchemy.orm import Session, joinedload

from src.models.accounts.user import User
from src.models.client.order import Order
from src.models.client.product_purchase import ProductPurchase
from src.models.client.service_booking import ServiceBooking
from src.models.provider.coach_profile.coach_profile import CoachProfile
from src.models.provider.product.coach_product import CoachProduct
from src.models.provider.service.coach_service import CoachService


def get_user_billing_orders(
    db: Session,
    user_id: int,
) -> list[Order]:
    """Retrieve all paid or refunded orders for the client in billing history."""
    return (
        db.query(Order)
        .options(
            joinedload(Order.coach),
            joinedload(Order.coach_profile).joinedload(CoachProfile.user),
            joinedload(Order.service_booking).joinedload(ServiceBooking.service),
            joinedload(Order.product_purchase).joinedload(ProductPurchase.product),
        )
        .filter(
            Order.user_id == user_id,
            Order.payment_status.in_(["paid", "refunded"]),
        )
        .order_by(Order.id.desc())
        .all()
    )


def get_user_billing_order_by_id(
    db: Session,
    user_id: int,
    order_id: int,
) -> Order | None:
    """Retrieve a single paid or refunded order by ID for the client."""
    return (
        db.query(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.coach),
            joinedload(Order.coach_profile).joinedload(CoachProfile.user),
            joinedload(Order.service_booking).joinedload(ServiceBooking.service),
            joinedload(Order.product_purchase).joinedload(ProductPurchase.product),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.payment_status.in_(["paid", "refunded"]),
        )
        .first()
    )

