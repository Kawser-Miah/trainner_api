from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.coach_profile_list_service import get_coach_profile_list_service

router = APIRouter(
    prefix=settings.coach_profile_list_prefix,
    tags=["Client Browse Coaches"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Coach Profile List",
    description="List approved coach profiles with optional search, category, and ordering filters.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_profile_list(
    request: Request,
    search: str | None = Query(default=None, description="Search by name, headline, or about"),
    category: str | None = Query(default=None, description="Filter by category ID or name"),
    ordering: str | None = Query(default=None, description="Order by rating, popular, etc."),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    profiles = await get_coach_profile_list_service(
        db=db,
        search=search,
        category=category,
        ordering=ordering,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach profiles retrieved successfully.",
        data=profiles,
    )
