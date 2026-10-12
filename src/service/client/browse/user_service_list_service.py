from fastapi import Request
from sqlalchemy.orm import Session

from src.models.provider.service.coach_service import CoachService
from src.repository.client.browse.client_browse_repository import get_browse_coach_services
from src.schemas.client.browse.service_schemas import (
    ClientServiceCategory,
    ClientServiceItemResponse,
    ClientServiceProviderDetails,
)
from src.service.client.browse.helpers import (
    format_iso_datetime,
    get_coach_provider_details,
)


def serialize_client_service_item(
    service: CoachService,
    request: Request | None = None,
) -> ClientServiceItemResponse:
    profile = service.coach_profile
    user = profile.user if profile else None
    prov_dict = get_coach_provider_details(profile, request) if profile else {}

    prov_obj = ClientServiceProviderDetails(
        id=prov_dict.get("id", user.id if user else 0),
        coach_profile_id=prov_dict.get("coach_profile_id", profile.id if profile else 0),
        full_name=prov_dict.get("full_name", ""),
        email=prov_dict.get("email", ""),
        phone_number=prov_dict.get("phone_number", ""),
        address=prov_dict.get("address"),
        rating=prov_dict.get("rating", 0.0),
        review_count=prov_dict.get("review_count", 0),
        headline=prov_dict.get("headline"),
        profile_photo=prov_dict.get("profile_photo"),
        about=prov_dict.get("about"),
    )

    cat_obj = None
    if service.category:
        cat_obj = ClientServiceCategory(
            id=service.category.id,
            name=service.category.name,
            description=service.category.description,
        )

    benefits_list = [b.outcome for b in (service.benefits or [])]

    return ClientServiceItemResponse(
        id=service.id,
        coach_id=user.id if user else profile.user_id if profile else 0,
        coach_profile_id=profile.id if profile else 0,
        provider_details=prov_obj,
        title=service.title,
        description=service.description or "",
        service_type=service.service_type,
        service_type_display="One Time Session" if service.service_type == "one_time" else service.service_type.title(),
        session_format=service.session_format,
        session_format_display="Video Call" if service.session_format == "video" else service.session_format.title(),
        session_duration=service.session_duration,
        currency=service.currency,
        price=service.price,
        booking_type=service.booking_type,
        booking_type_display="Instant Booking" if service.booking_type == "instant" else "Coach Approval Required",
        who_is_this_service_for=service.who_is_this_service_for or "",
        preparation_instructions=service.preparation_instructions or "",
        cancellation_policy=service.cancellation_policy,
        cancellation_policy_display=service.cancellation_policy.title(),
        session_url=service.session_url,
        status=service.status,
        category=cat_obj,
        benefits=benefits_list,
        created_at=format_iso_datetime(service.created_at),
        updated_at=format_iso_datetime(service.updated_at),
    )


async def get_user_service_list_service(
    db: Session,
    search: str | None = None,
    coach_profile: int | None = None,
    category_id: int | None = None,
    request: Request | None = None,
) -> list[ClientServiceItemResponse]:
    services = get_browse_coach_services(
        db=db,
        coach_profile_id=coach_profile,
        search=search,
        category_id=category_id,
        status="published",
    )
    return [serialize_client_service_item(s, request) for s in services]
