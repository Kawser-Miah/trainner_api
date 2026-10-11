import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import (
    CategoryNotFoundException,
    CoachProductNotFoundException,
    CoachProfileNotFoundException,
)
from src.models.accounts.user import User
from src.models.provider.product.coach_product import CoachProduct
from src.repository.provider.category_repository import get_category_by_id
from src.repository.provider.coach_profile.coach_profile_repository import (
    get_coach_profile_by_user_id,
)
from src.repository.provider.product.coach_product_repository import (
    create_coach_product,
    delete_coach_product,
    get_coach_product_by_id,
    get_coach_products_by_profile_id,
    update_coach_product,
)
from src.schemas.provider.product.coach_product import (
    CoachProductCategoryDetailsResponse,
    CoachProductDataResponse,
    DeleteCoachProductDataResponse,
)
from src.utils.media import build_media_url, delete_media_file, get_base_url


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def format_price_string(price: Any) -> str:
    if price is None:
        return "0.00"
    try:
        val_float = float(price)
        return f"{val_float:.2f}"
    except (ValueError, TypeError):
        return str(price)


async def save_product_thumbnail(file: Any) -> str | None:
    if not file or not hasattr(file, "filename") or not getattr(file, "filename", None):
        return None

    content = await file.read()
    if not content or len(content) == 0:
        return None

    ext = Path(file.filename).suffix or ".jpg"
    clean_stem = re.sub(r"[^\w\-]", "_", Path(file.filename).stem)
    unique_name = f"{clean_stem}_{uuid.uuid4().hex[:8]}{ext}"

    dest_dir = Path("media") / "coach" / "products"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / unique_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"/media/coach/products/{unique_name}"


async def save_product_book_file(file: Any) -> tuple[str | None, str | None]:
    if not file or not hasattr(file, "filename") or not getattr(file, "filename", None):
        return None, None

    content = await file.read()
    if not content or len(content) == 0:
        return None, None

    suffix = Path(file.filename).suffix or ".bin"
    file_type = suffix.lstrip(".").upper() or "PDF"
    clean_stem = re.sub(r"[^\w\-]", "_", Path(file.filename).stem)
    unique_name = f"{clean_stem}_{uuid.uuid4().hex[:8]}{suffix}"

    dest_dir = Path("media") / "coach" / "products" / "files"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / unique_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"/media/coach/products/files/{unique_name}", file_type


def build_download_url(product_id: int, request: Request | None) -> str:
    base = get_base_url(request)
    if not base:
        return f"/api/v1/user/digital-product-download/{product_id}/"
    return f"{base}/api/v1/user/digital-product-download/{product_id}/"


def map_product_to_response(
    product: CoachProduct,
    user_id: int,
    request: Request | None = None,
) -> CoachProductDataResponse:
    category_details = None
    if product.category:
        category_details = CoachProductCategoryDetailsResponse(
            id=product.category.id,
            name=product.category.name,
            description=product.category.description,
        )

    thumbnail_url = build_media_url(product.thumbnail, request)
    preview_url = build_media_url(product.preview_file, request) if product.preview_file else None
    download_url = build_download_url(product.id, request) if product.book_file else None

    return CoachProductDataResponse(
        id=product.id,
        coach=user_id,
        category=product.category_id,
        category_details=category_details,
        title=product.title,
        description=product.description,
        Thumbnail=thumbnail_url,
        download_url=download_url,
        preview_file=preview_url,
        page_count=product.page_count,
        preview_page_count=product.preview_page_count,
        file_type=product.file_type,
        price=product.price,
        status=product.status,
        sales_count=product.sales_count,
        revenue=product.revenue,
        created_at=format_dt(product.created_at),
        updated_at=format_dt(product.updated_at),
    )


async def create_provider_product(
    db: Session,
    user: User,
    *,
    title: str,
    category_id: int,
    description: str | None = None,
    price: str = "0.00",
    status: str = "published",
    thumbnail: Any = None,
    book_file: Any = None,
    preview_file: Any = None,
    page_count: int | None = None,
    preview_page_count: int | None = None,
    request: Request | None = None,
) -> CoachProductDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    category_obj = get_category_by_id(db, category_id)
    if category_obj is None:
        raise CategoryNotFoundException()

    thumbnail_path = await save_product_thumbnail(thumbnail)
    book_file_path, file_type = await save_product_book_file(book_file)
    preview_path, _ = await save_product_book_file(preview_file) if preview_file else (None, None)

    product = create_coach_product(
        db=db,
        coach_profile_id=profile.id,
        category_id=category_id,
        title=title,
        description=description,
        thumbnail=thumbnail_path,
        book_file=book_file_path,
        preview_file=preview_path,
        file_type=file_type,
        page_count=page_count,
        preview_page_count=preview_page_count,
        price=format_price_string(price),
        status=status,
    )

    return map_product_to_response(product, user_id=user.id, request=request)


async def get_provider_products_list(
    db: Session,
    user: User,
    status: str | None = None,
    request: Request | None = None,
) -> list[CoachProductDataResponse]:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    products = get_coach_products_by_profile_id(
        db=db,
        coach_profile_id=profile.id,
        status=status,
    )

    return [map_product_to_response(p, user_id=user.id, request=request) for p in products]


async def get_provider_product_detail(
    db: Session,
    user: User,
    product_id: int,
    request: Request | None = None,
) -> CoachProductDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    product = get_coach_product_by_id(db=db, product_id=product_id)
    if product is None or product.coach_profile_id != profile.id:
        raise CoachProductNotFoundException()

    return map_product_to_response(product, user_id=user.id, request=request)


async def update_provider_product(
    db: Session,
    user: User,
    product_id: int,
    *,
    title: str | None = None,
    category_id: int | None = None,
    description: str | None = None,
    price: str | None = None,
    status: str | None = None,
    thumbnail: Any = None,
    book_file: Any = None,
    preview_file: Any = None,
    page_count: int | None = None,
    preview_page_count: int | None = None,
    request: Request | None = None,
) -> CoachProductDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    product = get_coach_product_by_id(db=db, product_id=product_id)
    if product is None or product.coach_profile_id != profile.id:
        raise CoachProductNotFoundException()

    if category_id is not None:
        category_obj = get_category_by_id(db, category_id)
        if category_obj is None:
            raise CategoryNotFoundException()

    new_thumbnail_path = None
    if thumbnail is not None and getattr(thumbnail, "filename", None):
        uploaded_thumb = await save_product_thumbnail(thumbnail)
        if uploaded_thumb:
            if product.thumbnail:
                delete_media_file(product.thumbnail)
            new_thumbnail_path = uploaded_thumb

    new_book_file_path = None
    new_file_type = None
    if book_file is not None and getattr(book_file, "filename", None):
        uploaded_book, detected_type = await save_product_book_file(book_file)
        if uploaded_book:
            if product.book_file:
                delete_media_file(product.book_file)
            new_book_file_path = uploaded_book
            new_file_type = detected_type

    new_preview_file_path = None
    if preview_file is not None and getattr(preview_file, "filename", None):
        uploaded_preview, _ = await save_product_book_file(preview_file)
        if uploaded_preview:
            if product.preview_file:
                delete_media_file(product.preview_file)
            new_preview_file_path = uploaded_preview

    formatted_price = format_price_string(price) if price is not None else None

    updated_product = update_coach_product(
        db=db,
        product=product,
        category_id=category_id,
        title=title,
        description=description,
        thumbnail=new_thumbnail_path if new_thumbnail_path is not None else None,
        book_file=new_book_file_path if new_book_file_path is not None else None,
        preview_file=new_preview_file_path if new_preview_file_path is not None else None,
        file_type=new_file_type if new_file_type is not None else None,
        page_count=page_count,
        preview_page_count=preview_page_count,
        price=formatted_price,
        status=status,
    )

    return map_product_to_response(updated_product, user_id=user.id, request=request)


async def delete_provider_product(
    db: Session,
    user: User,
    product_id: int,
) -> DeleteCoachProductDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    product = get_coach_product_by_id(db=db, product_id=product_id)
    if product is None or product.coach_profile_id != profile.id:
        raise CoachProductNotFoundException()

    if product.thumbnail:
        delete_media_file(product.thumbnail)
    if product.book_file:
        delete_media_file(product.book_file)
    if product.preview_file:
        delete_media_file(product.preview_file)

    deleted_id = delete_coach_product(db=db, product=product)
    return DeleteCoachProductDataResponse(id=deleted_id)
