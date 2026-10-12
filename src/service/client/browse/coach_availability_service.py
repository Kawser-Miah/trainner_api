from sqlalchemy.orm import Session

from src.service.client.browse.coach_availability_date_service import (
    get_coach_availability_date_service,
)
from src.service.client.browse.coach_availability_month_service import (
    get_coach_availability_month_service,
)


async def get_coach_availability_service(
    coach_profile_id: int,
    db: Session,
    date_str: str | None = None,
    month_str: str | None = None,
    service_id: int | None = None,
) -> dict:
    if month_str:
        return await get_coach_availability_month_service(
            coach_profile_id=coach_profile_id,
            db=db,
            month_str=month_str,
            service_id=service_id,
        )
    return await get_coach_availability_date_service(
        coach_profile_id=coach_profile_id,
        db=db,
        date_str=date_str,
        service_id=service_id,
    )
