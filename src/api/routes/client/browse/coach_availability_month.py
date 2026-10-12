from fastapi import APIRouter, Depends, Path, Query, Request, status
from fastapi.routing import APIRoute
from starlette.routing import Match
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.coach_availability_month_service import (
    get_coach_availability_month_service,
)


class MonthAvailabilityRoute(APIRoute):
    def matches(self, scope):
        match, child = super().matches(scope)
        if match == Match.FULL:
            query = scope.get("query_string", b"").decode("utf-8")
            if "month=" not in query:
                return Match.NONE, {}
        return match, child


router = APIRouter(
    prefix=settings.client_coaches_prefix,
    tags=["Client Browse Availability"],
    route_class=MonthAvailabilityRoute,
)


@router.get(
    f"/{{coach_profile_id}}{settings.client_availability_prefix}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get Coach Available Dates by Month",
    description="Retrieve list of available dates in a month for a coach.",
)
@router.get(
    f"/{{coach_profile_id}}{settings.client_availability_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_availability_month(
    coach_profile_id: int = Path(..., description="Coach Profile ID"),
    month: str = Query(..., description="Month filter in YYYY-MM format"),
    service_id: int | None = Query(default=None, description="Service ID to calculate duration"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    data = await get_coach_availability_month_service(
        coach_profile_id=coach_profile_id,
        db=db,
        month_str=month,
        service_id=service_id,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Available dates retrieved successfully.",
        data=data,
    )
