from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import (
    get_browse_digital_product_detail,
    get_browse_other_products,
    is_product_purchased_by_user,
)
from src.service.client.browse.helpers import format_digital_product_dict


async def get_digital_product_detail_service(
    product_id: int,
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> dict:
    product = get_browse_digital_product_detail(db=db, product_id=product_id)
    if not product or product.status != "published":
        raise AppException(
            status=404,
            message="Digital product not found.",
            error="NOT_FOUND",
        )

    is_purchased = is_product_purchased_by_user(
        db=db,
        user_id=current_user.id,
        product=product,
    )

    product_dict = format_digital_product_dict(
        product=product,
        is_purchased=is_purchased,
        request=request,
    )

    other_products_models = get_browse_other_products(
        db=db,
        coach_profile_id=product.coach_profile_id,
        exclude_product_id=product.id,
        status="published",
    )

    other_products = []
    for op in other_products_models:
        op_purchased = is_product_purchased_by_user(
            db=db,
            user_id=current_user.id,
            product=op,
        )
        other_products.append(
            format_digital_product_dict(
                product=op,
                is_purchased=op_purchased,
                request=request,
            )
        )

    product_dict["other_products"] = other_products
    return product_dict
