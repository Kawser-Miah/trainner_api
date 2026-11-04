from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.favorite.favorite_service import (
    add_coach_favorite_service,
    get_user_favorites_service,
    remove_coach_favorite_service,
)

router = APIRouter(
    prefix=settings.user_favorites_prefix,
    tags=["Client Coach Favorites"],
)


@router.post(
    "/{coach_profile_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Add Coach to Favorites",
    description="Add a coach profile to the current user's favorites list.",
)
@router.post(
    "/{coach_profile_id}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
def add_coach_favorite(
    coach_profile_id: int = Path(..., description="ID of the coach profile to favorite"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    result = add_coach_favorite_service(
        db=db,
        user_id=current_user.id,
        coach_profile_id=coach_profile_id,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        status=status.HTTP_201_CREATED,
        message="Coach added to favorites.",
        data=result,
    )


@router.delete(
    "/{coach_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Remove Coach from Favorites",
    description="Remove a coach profile from the current user's favorites list.",
)
@router.delete(
    "/{coach_profile_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
def remove_coach_favorite(
    coach_profile_id: int = Path(..., description="ID of the coach profile to unfavorite"),
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    result = remove_coach_favorite_service(
        db=db,
        user_id=current_user.id,
        coach_profile_id=coach_profile_id,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach removed from favorites.",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Favorite Coaches",
    description="Retrieve all favorite coach profiles for the authenticated user.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
def get_favorite_coaches(
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = get_user_favorites_service(
        db=db,
        user_id=current_user.id,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Favorite coaches retrieved successfully.",
        data=data,
    )
