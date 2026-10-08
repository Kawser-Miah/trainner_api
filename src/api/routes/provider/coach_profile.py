from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_provider_role
from src.models.accounts.user import User
from src.service.provider.coach_profile_service import (
    create_provider_coach_profile,
    get_provider_coach_profile,
    update_provider_coach_profile,
)

router = APIRouter(
    prefix=settings.coach_profile_prefix,
    tags=["Provider Coach Profile"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Profile",
    description="Retrieve the authenticated provider's coach profile.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_profile(
    request: Request,
    current_user: User = Depends(require_provider_role),
    db: Session = Depends(get_db),
):
    data = await get_provider_coach_profile(
        db=db,
        user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach profile retrieved successfully.",
        data=data,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Create Coach Profile",
    description="Create a new coach profile for the authenticated provider using multipart/form-data. The user can provide only the intro video (introvideo / intro_video / introduction_video). Video duration and display duration are automatically extracted.",
)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def create_coach_profile(
    request: Request,
    current_user: User = Depends(require_provider_role),
    db: Session = Depends(get_db),
):
    data = await create_provider_coach_profile(
        db=db,
        user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        status=status.HTTP_201_CREATED,
        message="Coach profile created successfully.",
        data=data,
    )


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Update Coach Profile",
    description="Update the existing coach profile for the authenticated provider using multipart/form-data.",
)
@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def update_coach_profile(
    request: Request,
    current_user: User = Depends(require_provider_role),
    db: Session = Depends(get_db),
):
    data = await update_provider_coach_profile(
        db=db,
        user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach profile updated successfully.",
        data=data,
    )
