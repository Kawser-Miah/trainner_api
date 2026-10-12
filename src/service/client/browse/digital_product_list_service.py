from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import (
    get_browse_digital_products,
    is_product_purchased_by_user,
)
from src.service.client.browse.helpers import format_digital_product_dict


async def get_digital_product_list_service(
    db: Session,
    current_user: User,
    search: str | None = None,
    category_id: int | None = None,
    coach_profile_id: int | None = None,
    request: Request | None = None,
) -> list[dict]:
    products = get_browse_digital_products(
        db=db,
        coach_profile_id=coach_profile_id,
        category_id=category_id,
        search=search,
        status="published",
    )

    results = []
    for product in products:
        is_purchased = is_product_purchased_by_user(
            db=db,
            user_id=current_user.id,
            product=product,
        )
        results.append(
            format_digital_product_dict(
                product=product,
                is_purchased=is_purchased,
                request=request,
            )
        )

    return results
