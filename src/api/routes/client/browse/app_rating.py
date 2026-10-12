from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.browse.app_rating_schemas import AppRatingCreateRequest
from src.service.client.browse.app_rating_service import (
    get_app_rating_stats_service,
    get_app_ratings_list_service,
    submit_app_rating_service,
)

router = APIRouter(
    tags=["Client Browse App Ratings"],
)


@router.get(
    settings.app_rating_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get App Rating Stats",
    description="Retrieve app rating statistics including average rating, total ratings, and current user's rating.",
)
@router.get(
    f"{settings.app_rating_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_app_rating_stats(
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await get_app_rating_stats_service(db=db, current_user=current_user)
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="App rating stats retrieved successfully.",
        data=data,
    )


@router.post(
    settings.app_rating_prefix,
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Submit App Rating",
    description="Submit or update a rating and review for the app.",
)
@router.post(
    f"{settings.app_rating_prefix}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def submit_app_rating(
    payload: AppRatingCreateRequest,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await submit_app_rating_service(
        payload=payload,
        db=db,
        current_user=current_user,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        status=status.HTTP_201_CREATED,
        message="App rating submitted successfully.",
        data=data,
    )


@router.get(
    settings.app_ratings_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get App Ratings List",
    description="Retrieve list of all app ratings with reviewer details.",
)
@router.get(
    f"{settings.app_ratings_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_app_ratings_list(
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await get_app_ratings_list_service(
        db=db,
        current_user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="App ratings retrieved successfully.",
        data=data,
    )
