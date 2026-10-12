from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.user_service_list_service import get_user_service_list_service

router = APIRouter(
    prefix=settings.user_service_list_prefix,
    tags=["Client Browse Services"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="User Service List",
    description="List published coaching services with optional search and coach filtering.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_service_list(
    request: Request,
    search: str | None = Query(default=None, description="Search term for title or description"),
    coach_profile: int | None = Query(default=None, alias="coach_profile", description="Coach profile ID"),
    category: int | None = Query(default=None, alias="category", description="Category ID"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    services = await get_user_service_list_service(
        db=db,
        search=search,
        coach_profile=coach_profile,
        category_id=category,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Services retrieved successfully.",
        data=services,
    )
