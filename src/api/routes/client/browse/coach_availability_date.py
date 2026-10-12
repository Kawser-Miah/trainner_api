from fastapi import APIRouter, Depends, Path, Query, Request, status
from fastapi.routing import APIRoute
from starlette.routing import Match
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.coach_availability_date_service import (
    get_coach_availability_date_service,
)


class DateAvailabilityRoute(APIRoute):
    def matches(self, scope):
        match, child = super().matches(scope)
        if match == Match.FULL:
            query = scope.get("query_string", b"").decode("utf-8")
            if "month=" in query:
                return Match.NONE, {}
        return match, child


router = APIRouter(
    prefix=settings.client_coaches_prefix,
    tags=["Client Browse Availability"],
    route_class=DateAvailabilityRoute,
)


@router.get(
    f"/{{coach_profile_id}}{settings.client_availability_prefix}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Availability by Date",
    description="Retrieve available slots and on-call windows for a specific date.",
)
@router.get(
    f"/{{coach_profile_id}}{settings.client_availability_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_availability_date(
    coach_profile_id: int = Path(..., description="Coach Profile ID"),
    date: str | None = Query(default=None, description="Date filter in YYYY-MM-DD format"),
    service_id: int | None = Query(default=None, description="Service ID to calculate duration"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await get_coach_availability_date_service(
        coach_profile_id=coach_profile_id,
        db=db,
        date_str=date,
        service_id=service_id,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Availability retrieved successfully.",
        data=data,
    )
