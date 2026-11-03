from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.browse.coach_profile_review_schemas import (
    CoachProfileReviewCreateRequest,
)
from src.service.client.browse.coach_profile_review_service import (
    submit_coach_profile_review_service,
)

router = APIRouter(
    tags=["Client Browse Reviews"],
)


@router.post(
    f"{settings.coach_profile_review_prefix}/{{coach_profile_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Submit Coach Profile Review",
    description="Submit or update a rating and review for a coach profile.",
)
@router.post(
    f"{settings.coach_profile_review_prefix}/{{coach_profile_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def submit_coach_profile_review(
    payload: CoachProfileReviewCreateRequest,
    coach_profile_id: int = Path(..., description="Coach Profile ID"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await submit_coach_profile_review_service(
        db=db,
        current_user=current_user,
        coach_profile_id=coach_profile_id,
        payload=payload,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Rating submitted successfully.",
        data=data,
    )
