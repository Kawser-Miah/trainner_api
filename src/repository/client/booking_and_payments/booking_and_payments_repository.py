from sqlalchemy.orm import Session, joinedload

from src.models.client.service_order import ServiceOrder
from src.models.provider.coach_profile import CoachProfile
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
) -> list[ServiceOrder]:
    return (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.service))
        .filter(
            ServiceOrder.coach_profile_id == coach_profile_id,
            ServiceOrder.booking_date == booking_date,
            ServiceOrder.status.notin_(["cancelled", "rejected", "expired"]),
        )
        .all()
    )


def get_coach_orders_for_month(
    db: Session,
    coach_profile_id: int,
    month_prefix: str,
) -> list[ServiceOrder]:
    return (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.service))
        .filter(
            ServiceOrder.coach_profile_id == coach_profile_id,
            ServiceOrder.booking_date.startswith(month_prefix),
            ServiceOrder.status.notin_(["cancelled", "rejected", "expired"]),
        )
        .all()
    )


def create_service_order(db: Session, order: ServiceOrder) -> ServiceOrder:
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_service_order_by_id(db: Session, order_id: int) -> ServiceOrder | None:
    return (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.user),
            joinedload(ServiceOrder.coach),
            joinedload(ServiceOrder.coach_profile),
            joinedload(ServiceOrder.service).joinedload(CoachService.category),
            joinedload(ServiceOrder.product),
        )
        .filter(ServiceOrder.id == order_id)
        .first()
    )
