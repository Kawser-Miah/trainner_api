from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.coach_reviews_service import get_coach_reviews_service

router = APIRouter(
    prefix=settings.client_coaches_prefix,
    tags=["Client Browse Reviews"],
)


@router.get(
    f"/{{coach_profile_id}}{settings.client_reviews_prefix}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Reviews",
    description="Retrieve reviews, ratings, and rating breakdown for a coach.",
)
@router.get(
    f"/{{coach_profile_id}}{settings.client_reviews_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_reviews(
    coach_profile_id: int = Path(..., description="Coach Profile ID"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    reviews_data = await get_coach_reviews_service(
        coach_profile_id=coach_profile_id,
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Reviews retrieved successfully.",
        data=reviews_data,
    )
