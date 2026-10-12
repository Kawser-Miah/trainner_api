from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.coach_profile.coach_availability import CoachAvailability
from src.models.provider.coach_profile.coach_review import CoachReview
from src.models.provider.blog.coach_blog import CoachBlog
from src.models.provider.product.coach_product import CoachProduct
from src.models.provider.service.coach_service import CoachService


def get_client_categories(
    db: Session,
    is_active: bool = True,
) -> list[Category]:
    query = select(Category).where(Category.is_active == is_active).order_by(Category.id.asc())
    return list(db.execute(query).scalars().all())


def get_browse_coach_profiles(
    db: Session,
    search: str | None = None,
    category: str | None = None,
    ordering: str | None = None,
    recommended: bool = False,
) -> list[CoachProfile]:
    query = (
        select(CoachProfile)
        .join(CoachProfile.user)
        .where(CoachProfile.status == "approved")
        .options(
            selectinload(CoachProfile.user),
            selectinload(CoachProfile.categories),
            selectinload(CoachProfile.services),
            selectinload(CoachProfile.availability),
            selectinload(CoachProfile.reviews),
        )
    )

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                User.full_name.ilike(term),
                CoachProfile.headline.ilike(term),
                CoachProfile.about.ilike(term),
            )
        )

    if category and category.strip():
        cat_str = category.strip()
        if cat_str.isdigit():
            query = query.where(
                CoachProfile.categories.any(Category.id == int(cat_str))
            )
        else:
            query = query.where(
                CoachProfile.categories.any(Category.name.ilike(f"%{cat_str}%"))
            )

    if recommended:
        query = query.order_by(
            CoachProfile.avg_rating.desc(),
            CoachProfile.completed_sessions_count.desc(),
            CoachProfile.id.asc(),
        )
    elif ordering:
        order_key = ordering.strip().lower()
        if order_key in ["rating", "-rating", "avg_rating", "-avg_rating"]:
            query = query.order_by(CoachProfile.avg_rating.desc())
        elif order_key in ["popular", "sessions", "-sessions"]:
            query = query.order_by(CoachProfile.completed_sessions_count.desc())
        elif order_key in ["newest", "-created_at"]:
            query = query.order_by(CoachProfile.created_at.desc())
        elif order_key in ["oldest", "created_at"]:
            query = query.order_by(CoachProfile.created_at.asc())
        else:
            query = query.order_by(CoachProfile.id.asc())
    else:
        query = query.order_by(CoachProfile.id.asc())

    return list(db.execute(query).scalars().all())


def get_browse_coach_profile_detail(
    db: Session,
    coach_profile_id: int,
) -> CoachProfile | None:
    query = (
        select(CoachProfile)
        .where(CoachProfile.id == coach_profile_id)
        .options(
            selectinload(CoachProfile.user),
            selectinload(CoachProfile.categories),
            selectinload(CoachProfile.certifications),
            selectinload(CoachProfile.qualifications),
            selectinload(CoachProfile.availability),
            selectinload(CoachProfile.reviews).selectinload(CoachReview.user),
            selectinload(CoachProfile.services).selectinload(CoachService.benefits),
            selectinload(CoachProfile.services).selectinload(CoachService.category),
            selectinload(CoachProfile.blogs).selectinload(CoachBlog.category),
            selectinload(CoachProfile.products).selectinload(CoachProduct.category),
        )
    )
    return db.execute(query).scalar_one_or_none()


def get_browse_coach_services(
    db: Session,
    coach_profile_id: int | None = None,
    search: str | None = None,
    category_id: int | None = None,
    status: str = "published",
) -> list[CoachService]:
    query = (
        select(CoachService)
        .join(CoachService.coach_profile)
        .join(CoachProfile.user)
        .options(
            selectinload(CoachService.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachService.category),
            selectinload(CoachService.benefits),
        )
    )

    if status:
        query = query.where(CoachService.status == status)

    if coach_profile_id is not None:
        query = query.where(CoachService.coach_profile_id == coach_profile_id)

    if category_id is not None:
        query = query.where(CoachService.category_id == category_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                CoachService.title.ilike(term),
                CoachService.description.ilike(term),
                User.full_name.ilike(term),
            )
        )

    query = query.order_by(CoachService.id.asc())
    return list(db.execute(query).scalars().all())


def get_browse_coach_service_detail(
    db: Session,
    service_id: int,
) -> CoachService | None:
    query = (
        select(CoachService)
        .where(CoachService.id == service_id)
        .options(
            selectinload(CoachService.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachService.category),
            selectinload(CoachService.benefits),
        )
    )
    return db.execute(query).scalar_one_or_none()


def get_browse_coach_reviews(
    db: Session,
    coach_profile_id: int,
) -> list[CoachReview]:
    query = (
        select(CoachReview)
        .where(CoachReview.coach_profile_id == coach_profile_id)
        .options(selectinload(CoachReview.user))
        .order_by(CoachReview.created_at.desc())
    )
    return list(db.execute(query).scalars().all())


def get_browse_coach_availability(
    db: Session,
    coach_profile_id: int,
) -> CoachAvailability | None:
    query = select(CoachAvailability).where(CoachAvailability.coach_profile_id == coach_profile_id)
    return db.execute(query).scalar_one_or_none()


def is_product_purchased_by_user(
    db: Session,
    user_id: int,
    product: CoachProduct,
) -> bool:
    from src.models.client.product_purchase import ProductPurchase

    if product.coach_profile and product.coach_profile.user_id == user_id:
        return True

    query = select(ProductPurchase).where(
        ProductPurchase.user_id == user_id,
        ProductPurchase.product_id == product.id,
    )
    return db.execute(query).scalar_one_or_none() is not None


def get_browse_digital_products(
    db: Session,
    coach_profile_id: int | None = None,
    category_id: int | None = None,
    search: str | None = None,
    status: str = "published",
) -> list[CoachProduct]:
    query = (
        select(CoachProduct)
        .join(CoachProduct.coach_profile)
        .join(CoachProfile.user)
        .options(
            selectinload(CoachProduct.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachProduct.category),
        )
    )

    if status:
        query = query.where(CoachProduct.status == status)

    if coach_profile_id is not None:
        query = query.where(CoachProduct.coach_profile_id == coach_profile_id)

    if category_id is not None:
        query = query.where(CoachProduct.category_id == category_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                CoachProduct.title.ilike(term),
                CoachProduct.description.ilike(term),
                User.full_name.ilike(term),
            )
        )

    query = query.order_by(CoachProduct.id.asc())
    return list(db.execute(query).scalars().all())


def get_browse_digital_product_detail(
    db: Session,
    product_id: int,
) -> CoachProduct | None:
    query = (
        select(CoachProduct)
        .where(CoachProduct.id == product_id)
        .options(
            selectinload(CoachProduct.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachProduct.category),
        )
    )
    return db.execute(query).scalar_one_or_none()


def get_browse_other_products(
    db: Session,
    coach_profile_id: int,
    exclude_product_id: int,
    status: str = "published",
) -> list[CoachProduct]:
    query = (
        select(CoachProduct)
        .join(CoachProduct.coach_profile)
        .join(CoachProfile.user)
        .where(
            CoachProduct.coach_profile_id == coach_profile_id,
            CoachProduct.id != exclude_product_id,
        )
        .options(
            selectinload(CoachProduct.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachProduct.category),
        )
    )
    if status:
        query = query.where(CoachProduct.status == status)

    query = query.order_by(CoachProduct.id.asc())
    return list(db.execute(query).scalars().all())


def get_browse_blogs(
    db: Session,
    category_id: int | None = None,
    coach_profile_id: int | None = None,
    search: str | None = None,
    status: str = "published",
) -> list[CoachBlog]:
    query = (
        select(CoachBlog)
        .join(CoachBlog.coach_profile)
        .join(CoachProfile.user)
        .options(
            selectinload(CoachBlog.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachBlog.category),
        )
    )

    if status:
        query = query.where(CoachBlog.status == status)

    if category_id is not None:
        query = query.where(CoachBlog.category_id == category_id)

    if coach_profile_id is not None:
        query = query.where(CoachBlog.coach_profile_id == coach_profile_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                CoachBlog.title.ilike(term),
                CoachBlog.content.ilike(term),
                User.full_name.ilike(term),
            )
        )

    query = query.order_by(CoachBlog.id.desc())
    return list(db.execute(query).scalars().all())


def get_browse_blog_detail(
    db: Session,
    blog_id: int,
) -> CoachBlog | None:
    query = (
        select(CoachBlog)
        .where(CoachBlog.id == blog_id)
        .options(
            selectinload(CoachBlog.coach_profile).selectinload(CoachProfile.user),
            selectinload(CoachBlog.category),
        )
    )
    return db.execute(query).scalar_one_or_none()


