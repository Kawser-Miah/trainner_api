from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.database import get_db
from src.core.dependencies import require_approved_coach
from src.models.accounts.user import User
from src.core.config import settings
from src.schemas.provider.coach_profile.coach_availability import (
    UpdateCoachAvailabilityRequest,
)
from src.service.provider.coach_profile.coach_availability_service import (
    get_provider_coach_availability,
    update_provider_coach_availability,
)

router = APIRouter(
    prefix=settings.coach_availability_prefix,
    tags=["Provider Coach Availability"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Availability",
    description="Retrieve the authenticated provider's availability schedule.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_availability(
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_coach_availability(db=db, user=current_user)
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach availability retrieved successfully.",
        data=data,
    )


@router.put(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Update Coach Availability",
    description="Update the authenticated provider's availability schedule.",
)
@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def update_coach_availability(
    payload: UpdateCoachAvailabilityRequest,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await update_provider_coach_availability(
        db=db,
        user=current_user,
        payload=payload,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Availability updated successfully.",
        data=data,
    )
