from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.provider.category import Category


def get_category_by_id(
    db: Session,
    category_id: int,
) -> Category | None:
    return db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()


def get_categories_by_ids(
    db: Session,
    category_ids: list[int],
) -> list[Category]:
    if not category_ids:
        return []
    result = db.execute(
        select(Category).where(Category.id.in_(category_ids))
    )
    return list(result.scalars().all())


def get_or_create_default_categories(
    db: Session,
) -> list[Category]:
    """
    Ensure default categories exist in the database and return them.
    """
    existing = db.execute(select(Category)).scalars().all()
    if existing:
        return list(existing)

    defaults = [
        Category(name="Business", description="Business coaching", is_active=True),
        Category(name="Career", description="Career development and growth", is_active=True),
        Category(name="Fitness", description="Health and fitness coaching", is_active=True),
        Category(name="Life Coaching", description="Personal and life coaching", is_active=True),
    ]
    for cat in defaults:
        db.add(cat)
    db.flush()
    return defaults
