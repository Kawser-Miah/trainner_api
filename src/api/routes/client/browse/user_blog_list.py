from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.user_blog_list_service import get_user_blog_list_service

router = APIRouter(
    prefix=settings.user_blog_list_prefix,
    tags=["Client Browse Blogs"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="User Blog List",
    description="Retrieve published blogs for client browsing with optional category filter.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_blog_list(
    request: Request,
    category: int | None = Query(default=None, description="Category ID filter"),
    search: str | None = Query(default=None, description="Search term for title or content"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    blogs = await get_user_blog_list_service(
        db=db,
        current_user=current_user,
        category_id=category,
        search=search,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Blogs retrieved successfully.",
        data=blogs,
    )
