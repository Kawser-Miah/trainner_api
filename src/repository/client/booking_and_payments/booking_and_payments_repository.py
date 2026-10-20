from sqlalchemy.orm import Session, joinedload

from src.models.client.service_order import ServiceOrder
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.service import CoachService


def get_service_for_booking(db: Session, service_id: int) -> CoachService | None:
    return (
        db.query(CoachService)
        .options(
            joinedload(CoachService.category),
            joinedload(CoachService.coach_profile).joinedload(CoachProfile.user),
        )
        .filter(CoachService.id == service_id)
        .first()
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
        )
        .filter(ServiceOrder.id == order_id)
        .first()
    )
