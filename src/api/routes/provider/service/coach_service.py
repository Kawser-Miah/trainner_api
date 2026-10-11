from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_approved_coach
from src.models.accounts.user import User
from src.schemas.provider.service.coach_service import (
    CreateCoachServiceRequest,
    UpdateCoachServiceRequest,
)
from src.service.provider.service.coach_service_service import (
    create_provider_service,
    delete_provider_service,
    get_provider_service_detail,
    get_provider_services_list,
    update_provider_service,
)

router = APIRouter(
    prefix=settings.coach_services_prefix,
    tags=["Provider Coach Services"],
)


@router.post(
    settings.service_create_prefix,
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Create Coach Service",
    description="Create a new service offering for the authenticated approved coach.",
)
@router.post(
    f"{settings.service_create_prefix}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def create_service(
    payload: CreateCoachServiceRequest,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await create_provider_service(
        db=db,
        user=current_user,
        payload=payload,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_201_CREATED,
        message="Service created successfully.",
        data=data,
    )


@router.get(
    settings.service_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="List Coach Services",
    description="List all services for the authenticated approved coach, optionally filtered by status.",
)
@router.get(
    f"{settings.service_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def list_services(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_services_list(
        db=db,
        user=current_user,
        status=status_filter,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Services retrieved successfully.",
        data=data,
    )


@router.get(
    "/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Service Detail",
    description="Retrieve details of a specific service owned by the authenticated approved coach.",
)
@router.get(
    "/{service_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_service(
    service_id: int,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await get_provider_service_detail(
        db=db,
        user=current_user,
        service_id=service_id,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Service retrieved successfully.",
        data=data,
    )


@router.patch(
    "/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Update Coach Service",
    description="Update a specific service owned by the authenticated approved coach.",
)
@router.patch(
    "/{service_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def patch_service(
    service_id: int,
    payload: UpdateCoachServiceRequest,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await update_provider_service(
        db=db,
        user=current_user,
        service_id=service_id,
        payload=payload,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Service updated successfully.",
        data=data,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Delete Coach Service",
    description="Delete a specific service owned by the authenticated approved coach.",
)
@router.delete(
    "/{service_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def delete_service(
    service_id: int,
    current_user: User = Depends(require_approved_coach),
    db: Session = Depends(get_db),
):
    data = await delete_provider_service(
        db=db,
        user=current_user,
        service_id=service_id,
    )
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Service deleted successfully.",
        data=data,
    )
