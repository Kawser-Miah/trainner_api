from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.repository.client.browse.client_browse_repository import (
    get_browse_coach_service_detail,
    get_browse_coach_services,
)
from src.schemas.client.browse.service_schemas import ClientServiceDetailResponse
from src.service.client.browse.user_service_list_service import serialize_client_service_item


async def get_user_service_detail_service(
    service_id: int,
    db: Session,
    request: Request | None = None,
) -> ClientServiceDetailResponse:
    service = get_browse_coach_service_detail(db=db, service_id=service_id)
    if not service:
        raise AppException(
            message="Service not found.",
            status=404,
            error="SERVICE_NOT_FOUND",
        )

    base_item = serialize_client_service_item(service, request)

    # Fetch other services from the same coach
    other_services = get_browse_coach_services(
        db=db,
        coach_profile_id=service.coach_profile_id,
        status="published",
    )
    other_items = [
        serialize_client_service_item(s, request)
        for s in other_services
        if s.id != service.id
    ]

    return ClientServiceDetailResponse(
        **base_item.model_dump(),
        other_sessions=other_items,
    )
