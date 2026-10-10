from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_approved_coach
from src.models.accounts.user import User
from src.service.provider.coach_profile.coach_review_service import (
    get_provider_coach_reviews,
)

router = APIRouter(
    prefix=settings.coach_reviews_prefix,
    tags=["Provider Coach Reviews"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Reviews",
    description="Retrieve the authenticated provider's reviews and rating breakdown.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_reviews(
    request: Request,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_coach_reviews(
        db=db,
        user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Reviews retrieved successfully.",
        data=data,
    )
