from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.provider.product.coach_product import CoachProduct


def create_coach_product(
    db: Session,
    *,
    coach_profile_id: int,
    category_id: int,
    title: str,
    description: str | None = None,
    thumbnail: str | None = None,
    book_file: str | None = None,
    preview_file: str | None = None,
    file_type: str | None = None,
    page_count: int | None = None,
    preview_page_count: int | None = None,
    price: str = "0.00",
    status: str = "published",
) -> CoachProduct:
    product = CoachProduct(
        coach_profile_id=coach_profile_id,
        category_id=category_id,
        title=title,
        description=description,
        thumbnail=thumbnail,
        book_file=book_file,
        preview_file=preview_file,
        file_type=file_type,
        page_count=page_count,
        preview_page_count=preview_page_count,
        price=price,
        status=status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_coach_product_by_id(
    db: Session,
    product_id: int,
) -> CoachProduct | None:
    stmt = (
        select(CoachProduct)
        .where(CoachProduct.id == product_id)
        .options(
            selectinload(CoachProduct.category),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_coach_products_by_profile_id(
    db: Session,
    coach_profile_id: int,
    status: str | None = None,
) -> list[CoachProduct]:
    stmt = (
        select(CoachProduct)
        .where(CoachProduct.coach_profile_id == coach_profile_id)
        .options(
            selectinload(CoachProduct.category),
        )
    )
    if status is not None and status.strip():
        stmt = stmt.where(CoachProduct.status == status.strip())

    stmt = stmt.order_by(CoachProduct.id.desc())
    return list(db.execute(stmt).scalars().all())


def update_coach_product(
    db: Session,
    *,
    product: CoachProduct,
    category_id: int | None = None,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    book_file: str | None = None,
    preview_file: str | None = None,
    file_type: str | None = None,
    page_count: int | None = None,
    preview_page_count: int | None = None,
    price: str | None = None,
    status: str | None = None,
) -> CoachProduct:
    if category_id is not None:
        product.category_id = category_id
    if title is not None:
        product.title = title
    if description is not None:
        product.description = description
    if thumbnail is not None:
        product.thumbnail = thumbnail
    if book_file is not None:
        product.book_file = book_file
    if preview_file is not None:
        product.preview_file = preview_file
    if file_type is not None:
        product.file_type = file_type
    if page_count is not None:
        product.page_count = page_count
    if preview_page_count is not None:
        product.preview_page_count = preview_page_count
    if price is not None:
        product.price = price
    if status is not None:
        product.status = status

    db.commit()
    db.refresh(product)
    return product


def delete_coach_product(
    db: Session,
    product: CoachProduct,
) -> int:
    product_id = product.id
    db.delete(product)
    db.commit()
    return product_id
