from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.user_blog_detail_service import (
    get_user_blog_detail_service,
)

router = APIRouter(
    prefix=settings.user_blog_detail_prefix,
    tags=["Client Browse Blogs"],
)


@router.get(
    "/{blog_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="User Blog Detail",
    description="Retrieve detailed information about a published blog.",
)
@router.get(
    "/{blog_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_blog_detail(
    blog_id: int = Path(..., description="Blog ID"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    blog_detail = await get_user_blog_detail_service(
        blog_id=blog_id,
        db=db,
        current_user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Blog details retrieved successfully.",
        data=blog_detail,
    )
