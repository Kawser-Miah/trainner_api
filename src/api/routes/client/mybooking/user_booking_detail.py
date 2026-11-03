from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.mybooking.user_booking_detail_service import (
    get_user_booking_detail_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)


@router.get(
    f"{settings.user_booking_detail_prefix}/{{booking_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Booking Detail",
    description="Get one of the authenticated client's service bookings.",
)
@router.get(
    f"{settings.user_booking_detail_prefix}/{{booking_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_booking_detail(
    booking_id: int,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    booking = await get_user_booking_detail_service(
        db=db,
        current_user=current_user,
        booking_id=booking_id,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Booking details retrieved successfully.",
        data=booking,
    )

