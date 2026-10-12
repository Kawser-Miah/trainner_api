from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.digital_product_list_service import (
    get_digital_product_list_service,
)

router = APIRouter(
    prefix=settings.digital_product_list_prefix,
    tags=["Client Browse Digital Products"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Digital Product List",
    description="Retrieve list of published digital products for client browsing.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_digital_product_list(
    request: Request,
    search: str | None = Query(default=None, description="Search term for title or description"),
    category: int | None = Query(default=None, description="Category ID filter"),
    coach_profile: int | None = Query(default=None, description="Coach profile ID filter"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    products = await get_digital_product_list_service(
        db=db,
        current_user=current_user,
        search=search,
        category_id=category,
        coach_profile_id=coach_profile,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Digital products retrieved successfully.",
        data=products,
    )
