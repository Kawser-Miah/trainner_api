from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_approved_coach
from src.models.accounts.user import User
from src.service.provider.blog.coach_blog_service import (
    create_provider_blog,
    delete_provider_blog,
    get_provider_blog_detail,
    get_provider_blogs_list,
    update_provider_blog,
)

router = APIRouter(
    prefix=settings.coach_blogs_prefix,
    tags=["Provider Coach Blogs"],
)


@router.post(
    settings.blog_create_prefix,
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Create Coach Blog",
    description="Create a new blog post for the authenticated approved coach using multipart/form-data.",
)
@router.post(
    f"{settings.blog_create_prefix}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def create_blog(
    request: Request,
    title: str = Form(..., description="Blog post title"),
    category: int = Form(..., description="Category ID"),
    content: str = Form(..., description="Blog post content"),
    status_val: str = Form("published", alias="status", description="Blog status ('published' or 'draft')"),
    image: UploadFile | None = File(None, description="Optional featured image file"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await create_provider_blog(
        db=db,
        user=current_user,
        title=title,
        category_id=category,
        content=content,
        status=status_val,
        image=image,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_201_CREATED,
        message="Blog created successfully.",
        data=data,
    )


@router.get(
    settings.blog_create_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="List Coach Blogs",
    description="List all blog posts for the authenticated approved coach, optionally filtered by status.",
)
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    settings.blog_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    f"{settings.blog_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def list_blogs(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_blogs_list(
        db=db,
        user=current_user,
        status=status_filter,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Blogs retrieved successfully.",
        data=data,
    )


@router.get(
    "/{blog_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Blog Detail",
    description="Retrieve details of a specific blog post owned by the authenticated approved coach.",
)
@router.get(
    "/{blog_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_blog(
    blog_id: int,
    request: Request,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_blog_detail(
        db=db,
        user=current_user,
        blog_id=blog_id,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Blog retrieved successfully.",
        data=data,
    )


@router.patch(
    "/{blog_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Update Coach Blog",
    description="Update a specific blog post owned by the authenticated approved coach using multipart/form-data.",
)
@router.patch(
    "/{blog_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def patch_blog(
    blog_id: int,
    request: Request,
    title: str | None = Form(None, description="Updated blog title"),
    category: int | None = Form(None, description="Updated category ID"),
    content: str | None = Form(None, description="Updated blog content"),
    status_val: str | None = Form(None, alias="status", description="Updated status"),
    image: UploadFile | None = File(None, description="Updated image file"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await update_provider_blog(
        db=db,
        user=current_user,
        blog_id=blog_id,
        title=title,
        category_id=category,
        content=content,
        status=status_val,
        image=image,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Blog updated successfully.",
        data=data,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Delete Coach Blog",
    description="Delete a specific blog post owned by the authenticated approved coach.",
)
@router.delete(
    "/{blog_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def delete_blog(
    blog_id: int,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await delete_provider_blog(
        db=db,
        user=current_user,
        blog_id=blog_id,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Blog deleted successfully.",
        data=data,
    )
