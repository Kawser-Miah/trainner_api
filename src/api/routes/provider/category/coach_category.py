from src.core.dependencies import require_approved_coach
from src.models.accounts.user import User
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.service.provider.category.category_service import list_categories_service

router = APIRouter(
    tags=["Provider Categories"],
)


@router.get(
    settings.category_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="List Categories",
    description="Retrieve all categories with their details and image URLs.",
)
@router.get(
    f"{settings.category_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    "/categories",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    "/categories/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def list_categories(
    request: Request,
    is_active: bool | None = Query(default=None, description="Filter categories by active status"),
    current_user: User = Depends(require_approved_coach),

    db: Session = Depends(get_db),
):
    categories = await list_categories_service(
        db=db,
        request=request,
        is_active=is_active,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Categories retrieved successfully.",
        data=categories,
    )
