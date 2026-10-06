from src.core.common_responses import CommonResponse
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.accounts.user import User
from src.service.auth.me import get_user_profile, update_user_profile


router = APIRouter(
    prefix=settings.me_prefix,
    tags=["User Profile"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_my_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    profile = get_user_profile(user=current_user, request=request)

    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Profile retrieved successfully.",
        data=profile,
    )


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def update_my_profile(
    request: Request,
    full_name: str | None = Form(None),
    phone_number: str | None = Form(None),
    address: str | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Fallback to alternative form field keys if needed
    if phone_number is None:
        try:
            form = await request.form()
            if "phone" in form:
                phone_number = str(form["phone"])
        except Exception:
            pass

    if image is None:
        try:
            form = await request.form()
            if "photo" in form and hasattr(form["photo"], "filename"):
                image = form["photo"]
        except Exception:
            pass

    profile = await update_user_profile(
        db=db,
        user=current_user,
        full_name=full_name,
        phone_number=phone_number,
        address=address,
        image=image,
        request=request,
    )

    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Profile updated successfully.",
        data=profile,
    )
