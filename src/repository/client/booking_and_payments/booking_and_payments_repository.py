from sqlalchemy.orm import Session, joinedload

from src.models.client.order import Order
from src.models.client.product_purchase import ProductPurchase
from src.models.client.service_booking import ServiceBooking
from src.models.client.service_order import ServiceOrder
from src.models.provider.coach_profile import CoachProfile, CoachReview
from src.models.provider.product import CoachProduct
from src.models.provider.service import CoachService


def get_product_for_purchase(db: Session, product_id: int) -> CoachProduct | None:
    return (
        db.query(CoachProduct)
        .options(
            joinedload(CoachProduct.category),
            joinedload(CoachProduct.coach_profile).joinedload(CoachProfile.user),
        )
        .filter(CoachProduct.id == product_id)
        .first()
    )


def get_service_for_booking(db: Session, service_id: int) -> CoachService | None:
    return (
        db.query(CoachService)
        .options(
            joinedload(CoachService.category),
            joinedload(CoachService.coach_profile).joinedload(CoachProfile.user),
            joinedload(CoachService.coach_profile).joinedload(CoachProfile.availability),
        )
        .filter(CoachService.id == service_id)
        .first()
    )


def get_coach_orders_for_date(
    db: Session,
    coach_profile_id: int,
    booking_date: str,
) -> list[Order]:
    return (
        db.query(Order)
        .join(Order.service_booking)
        .options(
            joinedload(Order.service_booking).joinedload(ServiceBooking.service),
        )
        .filter(
            Order.coach_profile_id == coach_profile_id,
            ServiceBooking.booking_date == booking_date,
            Order.status.notin_(["cancelled", "rejected", "expired"]),
        )
        .all()
    )


def get_coach_orders_for_month(
    db: Session,
    coach_profile_id: int,
    month_prefix: str,
) -> list[Order]:
    return (
        db.query(Order)
        .join(Order.service_booking)
        .options(
            joinedload(Order.service_booking).joinedload(ServiceBooking.service),
        )
        .filter(
            Order.coach_profile_id == coach_profile_id,
            ServiceBooking.booking_date.startswith(month_prefix),
            Order.status.notin_(["cancelled", "rejected", "expired"]),
        )
        .all()
    )


def create_service_order(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_service_order_by_id(db: Session, order_id: int) -> Order | None:
    return (
        db.query(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.coach),
            joinedload(Order.coach_profile),
            joinedload(Order.service_booking).joinedload(ServiceBooking.service).joinedload(CoachService.category),
            joinedload(Order.product_purchase).joinedload(ProductPurchase.product),
        )
        .filter(Order.id == order_id)
        .first()
    )


def get_user_service_orders(
    db: Session,
    user_id: int,
    statuses: list[str] | None = None,
) -> list[Order]:
    query = (
        db.query(Order)
        .join(Order.service_booking)
        .options(
            joinedload(Order.coach),
            joinedload(Order.coach_profile),
            joinedload(Order.service_booking).joinedload(ServiceBooking.service).joinedload(CoachService.category),
        )
        .filter(
            Order.user_id == user_id,
            Order.order_type == "service",
        )
    )
    if statuses:
        query = query.filter(Order.status.in_(statuses))
    return query.order_by(Order.id.desc()).all()


def get_reviewed_coach_profile_ids(
    db: Session,
    user_id: int,
    coach_profile_ids: list[int],
) -> set[int]:
    if not coach_profile_ids:
        return set()
    rows = (
        db.query(CoachReview.coach_profile_id)
        .filter(
            CoachReview.user_id == user_id,
            CoachReview.coach_profile_id.in_(coach_profile_ids),
        )
        .all()
    )
    return {row[0] for row in rows}


def get_user_service_order_by_id(
    db: Session,
    user_id: int,
    order_id: int,
) -> Order | None:
    return (
        db.query(Order)
        .join(Order.service_booking)
        .options(
            joinedload(Order.coach),
            joinedload(Order.coach_profile),
            joinedload(Order.service_booking).joinedload(ServiceBooking.service).joinedload(CoachService.category),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.order_type == "service",
        )
        .first()
    )
