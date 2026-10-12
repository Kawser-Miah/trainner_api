import calendar
from datetime import date
from sqlalchemy.orm import Session

from src.repository.client.browse.client_browse_repository import (
    get_browse_coach_availability,
    get_browse_coach_service_detail,
)
from src.schemas.client.browse.availability_schemas import (
    CoachMonthAvailabilityResponse,
)


async def get_coach_availability_month_service(
    coach_profile_id: int,
    db: Session,
    month_str: str | None = None,
    service_id: int | None = None,
) -> dict:
    availability = get_browse_coach_availability(db=db, coach_profile_id=coach_profile_id)
    session_duration = 60
    if service_id:
        service = get_browse_coach_service_detail(db=db, service_id=service_id)
        if service and service.session_duration:
            session_duration = service.session_duration

    weekly = availability.weekly if availability and availability.weekly else []
    on_call_enabled = bool(availability.on_call_enabled) if availability else True
    time_off = availability.time_off if availability and availability.time_off else []
    time_off_dates = {t.get("date") for t in time_off if isinstance(t, dict) and t.get("date")}

    if not weekly:
        weekly = [
            {"weekday": i, "start_time": "09:00", "end_time": "17:00"}
            for i in range(5)
        ]

    target_month_str = month_str or date.today().strftime("%Y-%m")
    try:
        year_val, month_val = map(int, target_month_str.strip().split("-"))
    except ValueError:
        year_val, month_val = 2026, 10

    _, num_days = calendar.monthrange(year_val, month_val)
    available_weekdays = {w.get("weekday") for w in weekly if isinstance(w, dict) and "weekday" in w}

    available_dates = []
    for day in range(1, num_days + 1):
        d = date(year_val, month_val, day)
        date_key = d.isoformat()
        if d.weekday() in available_weekdays and date_key not in time_off_dates:
            available_dates.append(date_key)

    return CoachMonthAvailabilityResponse(
        coach_profile_id=coach_profile_id,
        session_duration=session_duration,
        has_availability=bool(available_dates),
        takes_on_call=on_call_enabled,
        month=f"{year_val:04d}-{month_val:02d}",
        available_dates=available_dates,
    ).model_dump()
