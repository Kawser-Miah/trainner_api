from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_approved_coach
from src.core.exceptions import CoachProductNotFoundException
from src.models.accounts.user import User
from src.utils.uploads import resolve_media_path
from src.repository.provider.coach_profile.coach_profile_repository import get_coach_profile_by_user_id
from src.repository.provider.product.coach_product_repository import get_coach_product_by_id
from src.service.provider.product.coach_product_service import (
    create_provider_product,
    delete_provider_product,
    get_provider_product_detail,
    get_provider_products_list,
    update_provider_product,
)

router = APIRouter(
    tags=["Provider Coach Products"],
)


@router.post(
    f"{settings.coach_products_prefix}{settings.product_create_prefix}",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Create Coach Product",
    description="Create a new digital product for the authenticated approved coach using multipart/form-data.",
)
@router.post(
    f"{settings.coach_products_prefix}{settings.product_create_prefix}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def create_product(
    request: Request,
    title: str = Form(..., description="Product title"),
    category: int = Form(..., description="Category ID"),
    description: str | None = Form(None, description="Product description"),
    price: str = Form("0.00", description="Product price string (e.g. '19.00')"),
    status_val: str = Form("published", alias="status", description="Product status ('published' or 'draft')"),
    page_count: int | None = Form(None, description="Total page count"),
    preview_page_count: int | None = Form(None, description="Preview page count"),
    Thumbnail: UploadFile | None = File(None, description="Thumbnail / cover image"),
    thumbnail: UploadFile | None = File(None, description="Alternative alias for Thumbnail"),
    book_file: UploadFile | None = File(None, description="Digital product file (e.g. PDF)"),
    preview_file: UploadFile | None = File(None, description="Optional preview file"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    chosen_thumbnail = Thumbnail or thumbnail
    data = await create_provider_product(
        db=db,
        user=current_user,
        title=title,
        category_id=category,
        description=description,
        price=price,
        status=status_val,
        thumbnail=chosen_thumbnail,
        book_file=book_file,
        preview_file=preview_file,
        page_count=page_count,
        preview_page_count=preview_page_count,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_201_CREATED,
        message="Product created successfully.",
        data=data,
    )


@router.get(
    settings.product_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="List Coach Products",
    description="List all digital products for the authenticated approved coach, optionally filtered by status.",
)
@router.get(
    f"{settings.product_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    settings.coach_products_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    f"{settings.coach_products_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    f"{settings.coach_products_prefix}{settings.product_create_prefix}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
@router.get(
    f"{settings.coach_products_prefix}{settings.product_create_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def list_products(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_products_list(
        db=db,
        user=current_user,
        status=status_filter,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Products retrieved successfully.",
        data=data,
    )


@router.get(
    f"{settings.coach_products_prefix}/{{product_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Product Detail",
    description="Retrieve details of a specific digital product owned by the authenticated approved coach.",
)
@router.get(
    f"{settings.coach_products_prefix}/{{product_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_product(
    product_id: int,
    request: Request,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_product_detail(
        db=db,
        user=current_user,
        product_id=product_id,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Product retrieved successfully.",
        data=data,
    )


@router.patch(
    f"{settings.coach_products_prefix}/{{product_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Update Coach Product",
    description="Update a specific digital product owned by the authenticated approved coach using multipart/form-data.",
)
@router.patch(
    f"{settings.coach_products_prefix}/{{product_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def patch_product(
    product_id: int,
    request: Request,
    title: str | None = Form(None, description="Updated product title"),
    category: int | None = Form(None, description="Updated category ID"),
    description: str | None = Form(None, description="Updated description"),
    price: str | None = Form(None, description="Updated price"),
    status_val: str | None = Form(None, alias="status", description="Updated status"),
    page_count: int | None = Form(None, description="Updated page count"),
    preview_page_count: int | None = Form(None, description="Updated preview page count"),
    Thumbnail: UploadFile | None = File(None, description="Updated thumbnail file"),
    thumbnail: UploadFile | None = File(None, description="Updated thumbnail file alias"),
    book_file: UploadFile | None = File(None, description="Updated digital book file"),
    preview_file: UploadFile | None = File(None, description="Updated preview file"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    chosen_thumbnail = Thumbnail or thumbnail
    data = await update_provider_product(
        db=db,
        user=current_user,
        product_id=product_id,
        title=title,
        category_id=category,
        description=description,
        price=price,
        status=status_val,
        thumbnail=chosen_thumbnail,
        book_file=book_file,
        preview_file=preview_file,
        page_count=page_count,
        preview_page_count=preview_page_count,
        request=request,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Product updated successfully.",
        data=data,
    )


@router.delete(
    f"{settings.coach_products_prefix}/{{product_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Delete Coach Product",
    description="Delete a specific digital product owned by the authenticated approved coach.",
)
@router.delete(
    f"{settings.coach_products_prefix}/{{product_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await delete_provider_product(
        db=db,
        user=current_user,
        product_id=product_id,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Product deleted successfully.",
        data=data,
    )


download_router = APIRouter(
    tags=["Digital Product Download"],
)


@download_router.get(
    "/v1/user/digital-product-download/{product_id}",
    summary="Download Digital Product",
    description="Download the product file for a given product ID.",
    response_class=FileResponse,
)
@download_router.get(
    "/v1/user/digital-product-download/{product_id}/",
    include_in_schema=False,
    response_class=FileResponse,
)
async def download_product_file(
    product_id: int,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    # Only the coach who owns the product may fetch the full file through this route;
    # buyers go through the client download route.
    profile = get_coach_profile_by_user_id(db, current_user.id)
    product = get_coach_product_by_id(db=db, product_id=product_id)
    if (
        profile is None
        or product is None
        or product.coach_profile_id != profile.id
        or not product.book_file
    ):
        raise CoachProductNotFoundException()

    file_path = resolve_media_path(product.book_file)
    if file_path is None or not file_path.is_file():
        raise CoachProductNotFoundException()

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )
