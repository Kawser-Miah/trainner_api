from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.booking_and_payments.user_booking_list_service import (
    get_user_booking_list_service,
)

router = APIRouter(
    prefix=settings.user_booking_list_prefix,
    tags=["Client Booking & Payments"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="My Bookings",
    description=(
        "List the authenticated client's service bookings. "
        "status: upcoming|pending|confirmed|completed|cancelled|rejected (comma separated allowed)."
    ),
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_booking_list(
    request: Request,
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="upcoming|pending|confirmed|completed|cancelled|rejected (comma separated allowed)",
    ),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    bookings = await get_user_booking_list_service(
        db=db,
        current_user=current_user,
        status=status_filter,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="User bookings retrieved successfully.",
        data=bookings,
    )
