from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from src.core.exceptions import (
    CategoryNotFoundException,
    CoachProfileNotFoundException,
    CoachServiceNotFoundException,
)
from src.models.accounts.user import User
from src.models.provider.service.coach_service import CoachService
from src.repository.provider.category_repository import get_category_by_id
from src.repository.provider.coach_profile.coach_profile_repository import (
    get_coach_profile_by_user_id,
)
from src.repository.provider.service.coach_service_repository import (
    create_coach_service,
    delete_coach_service,
    get_coach_service_by_id,
    get_coach_services_by_profile_id,
    update_coach_service,
)
from src.schemas.provider.service.coach_service import (
    CoachServiceDataResponse,
    CreateCoachServiceRequest,
    ServiceBenefitResponse,
    ServiceCategoryResponse,
    UpdateCoachServiceRequest,
)


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def map_service_to_response(
    service: CoachService,
    user_id: int,
) -> CoachServiceDataResponse:
    category_resp = None
    if service.category:
        category_resp = ServiceCategoryResponse(
            id=service.category.id,
            name=service.category.name,
            description=service.category.description,
        )

    benefits_resp = [
        ServiceBenefitResponse(
            id=b.id,
            outcome=b.outcome,
        )
        for b in (service.benefits or [])
    ]

    return CoachServiceDataResponse(
        id=service.id,
        coach=user_id,
        title=service.title,
        description=service.description,
        service_type=service.service_type,
        session_format=service.session_format,
        session_duration=service.session_duration,
        currency=service.currency,
        price=service.price,
        booking_type=service.booking_type,
        who_is_this_service_for=service.who_is_this_service_for,
        preparation_instructions=service.preparation_instructions,
        cancellation_policy=service.cancellation_policy,
        session_url=service.session_url,
        status=service.status,
        benefits=benefits_resp,
        category=category_resp,
        bookings_count=service.bookings_count,
        revenue=service.revenue,
        created_at=format_dt(service.created_at),
        updated_at=format_dt(service.updated_at),
    )


async def create_provider_service(
    db: Session,
    user: User,
    payload: CreateCoachServiceRequest,
) -> CoachServiceDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    category = get_category_by_id(db, payload.category)
    if category is None:
        raise CategoryNotFoundException()

    benefits_data = [
        {"outcome": b.outcome}
        for b in (payload.benefits or [])
    ]

    service = create_coach_service(
        db,
        coach_profile_id=profile.id,
        category_id=payload.category,
        title=payload.title,
        description=payload.description,
        service_type=payload.service_type,
        session_format=payload.session_format,
        session_duration=payload.session_duration,
        currency=payload.currency,
        price=payload.price,
        booking_type=payload.booking_type,
        who_is_this_service_for=payload.who_is_this_service_for,
        preparation_instructions=payload.preparation_instructions,
        cancellation_policy=payload.cancellation_policy,
        session_url=payload.session_url,
        status=payload.status,
        benefits_data=benefits_data,
    )

    return map_service_to_response(service, user_id=user.id)


async def get_provider_services_list(
    db: Session,
    user: User,
    status: str | None = None,
) -> list[CoachServiceDataResponse]:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    services = get_coach_services_by_profile_id(
        db,
        coach_profile_id=profile.id,
        status=status,
    )
    return [map_service_to_response(s, user_id=user.id) for s in services]


async def get_provider_service_detail(
    db: Session,
    user: User,
    service_id: int,
) -> CoachServiceDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    service = get_coach_service_by_id(db, service_id)
    if service is None or service.coach_profile_id != profile.id:
        raise CoachServiceNotFoundException()

    return map_service_to_response(service, user_id=user.id)


async def update_provider_service(
    db: Session,
    user: User,
    service_id: int,
    payload: UpdateCoachServiceRequest,
) -> CoachServiceDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    service = get_coach_service_by_id(db, service_id)
    if service is None or service.coach_profile_id != profile.id:
        raise CoachServiceNotFoundException()

    if payload.category is not None:
        category = get_category_by_id(db, payload.category)
        if category is None:
            raise CategoryNotFoundException()

    update_dict = payload.model_dump(
        exclude_unset=True,
        exclude={"benefits", "category"},
    )
    if payload.category is not None:
        update_dict["category_id"] = payload.category

    benefits_data = None
    if payload.benefits is not None:
        benefits_data = [{"outcome": b.outcome} for b in payload.benefits]

    updated_service = update_coach_service(
        db,
        service=service,
        update_data=update_dict,
        benefits_data=benefits_data,
    )

    return map_service_to_response(updated_service, user_id=user.id)


async def delete_provider_service(
    db: Session,
    user: User,
    service_id: int,
) -> dict[str, int]:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    service = get_coach_service_by_id(db, service_id)
    if service is None or service.coach_profile_id != profile.id:
        raise CoachServiceNotFoundException()

    delete_coach_service(db, service)
    return {"id": service_id}
