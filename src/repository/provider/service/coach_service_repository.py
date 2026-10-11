from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.provider.service.coach_service import CoachService, CoachServiceBenefit


def create_coach_service(
    db: Session,
    *,
    coach_profile_id: int,
    category_id: int,
    title: str,
    description: str | None = None,
    service_type: str = "one_time",
    session_format: str = "video",
    session_duration: int = 60,
    currency: str = "USD",
    price: str = "0.00",
    booking_type: str = "instant",
    who_is_this_service_for: str | None = None,
    preparation_instructions: str | None = None,
    cancellation_policy: str = "standard",
    session_url: str | None = None,
    status: str = "published",
    benefits_data: list[dict[str, str]] | None = None,
) -> CoachService:
    service = CoachService(
        coach_profile_id=coach_profile_id,
        category_id=category_id,
        title=title,
        description=description,
        service_type=service_type,
        session_format=session_format,
        session_duration=session_duration,
        currency=currency,
        price=price,
        booking_type=booking_type,
        who_is_this_service_for=who_is_this_service_for,
        preparation_instructions=preparation_instructions,
        cancellation_policy=cancellation_policy,
        session_url=session_url,
        status=status,
    )
    db.add(service)
    db.flush()

    if benefits_data:
        for b in benefits_data:
            outcome = b.get("outcome", "").strip()
            if outcome:
                benefit = CoachServiceBenefit(
                    service_id=service.id,
                    outcome=outcome,
                )
                db.add(benefit)
        db.flush()

    db.commit()
    db.refresh(service)
    return service


def get_coach_service_by_id(
    db: Session,
    service_id: int,
) -> CoachService | None:
    stmt = (
        select(CoachService)
        .where(CoachService.id == service_id)
        .options(
            selectinload(CoachService.benefits),
            selectinload(CoachService.category),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_coach_services_by_profile_id(
    db: Session,
    coach_profile_id: int,
    status: str | None = None,
) -> list[CoachService]:
    stmt = (
        select(CoachService)
        .where(CoachService.coach_profile_id == coach_profile_id)
        .options(
            selectinload(CoachService.benefits),
            selectinload(CoachService.category),
        )
    )
    if status is not None and status.strip():
        stmt = stmt.where(CoachService.status == status.strip())

    stmt = stmt.order_by(CoachService.id.desc())
    return list(db.execute(stmt).scalars().all())


def update_coach_service(
    db: Session,
    *,
    service: CoachService,
    update_data: dict[str, Any],
    benefits_data: list[dict[str, str]] | None = None,
) -> CoachService:
    for field, val in update_data.items():
        if hasattr(service, field) and val is not None:
            setattr(service, field, val)

    if benefits_data is not None:
        service.benefits.clear()
        db.flush()
        for b in benefits_data:
            outcome = b.get("outcome", "").strip()
            if outcome:
                benefit = CoachServiceBenefit(
                    service_id=service.id,
                    outcome=outcome,
                )
                db.add(benefit)
        db.flush()

    db.commit()
    db.refresh(service)
    return service


def delete_coach_service(
    db: Session,
    service: CoachService,
) -> None:
    db.delete(service)
    db.commit()
