from typing import Any
from sqlalchemy.orm import Session

from src.core.exceptions import CoachProfileNotFoundException
from src.models.accounts.user import User
from src.repository.provider.coach_profile.coach_availability_repository import (
    create_or_update_coach_availability,
    get_coach_availability_by_profile_id,
)
from src.repository.provider.coach_profile.coach_profile_repository import (
    get_coach_profile_by_user_id,
)
from src.schemas.provider.coach_profile.coach_availability import (
    AvailabilityTimeOffItem,
    AvailabilityTimeSlotItem,
    CoachAvailabilityDataResponse,
    UpdateCoachAvailabilityRequest,
    get_weekday_display,
)


def format_availability_response(
    availability: Any | None,
) -> CoachAvailabilityDataResponse:
    if not availability:
        return CoachAvailabilityDataResponse(
            has_availability=False,
            weekly=[],
            on_call=[],
            on_call_enabled=True,
            time_off=[],
        )

    weekly_list: list[AvailabilityTimeSlotItem] = []
    for item in availability.weekly or []:
        wday = item.get("weekday", 0)
        wdisp = item.get("weekday_display") or get_weekday_display(wday)
        weekly_list.append(
            AvailabilityTimeSlotItem(
                weekday=wday,
                weekday_display=wdisp,
                start_time=item.get("start_time", ""),
                end_time=item.get("end_time", ""),
            )
        )

    on_call_list: list[AvailabilityTimeSlotItem] = []
    for item in availability.on_call or []:
        wday = item.get("weekday", 0)
        wdisp = item.get("weekday_display") or get_weekday_display(wday)
        on_call_list.append(
            AvailabilityTimeSlotItem(
                weekday=wday,
                weekday_display=wdisp,
                start_time=item.get("start_time", ""),
                end_time=item.get("end_time", ""),
            )
        )

    time_off_list: list[AvailabilityTimeOffItem] = []
    for item in availability.time_off or []:
        time_off_list.append(
            AvailabilityTimeOffItem(
                date=item.get("date", ""),
                reason=item.get("reason", ""),
            )
        )

    has_avail = bool(weekly_list or on_call_list)

    return CoachAvailabilityDataResponse(
        has_availability=has_avail,
        weekly=weekly_list,
        on_call=on_call_list,
        on_call_enabled=availability.on_call_enabled,
        time_off=time_off_list,
    )


async def get_provider_coach_availability(
    db: Session,
    user: User,
) -> CoachAvailabilityDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    availability = get_coach_availability_by_profile_id(db, profile.id)
    return format_availability_response(availability)


async def update_provider_coach_availability(
    db: Session,
    user: User,
    payload: UpdateCoachAvailabilityRequest,
) -> CoachAvailabilityDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    weekly_data = []
    for slot in payload.weekly:
        wdisp = slot.weekday_display or get_weekday_display(slot.weekday)
        weekly_data.append({
            "weekday": slot.weekday,
            "weekday_display": wdisp,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        })

    on_call_data = []
    for slot in payload.on_call:
        wdisp = slot.weekday_display or get_weekday_display(slot.weekday)
        on_call_data.append({
            "weekday": slot.weekday,
            "weekday_display": wdisp,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        })

    time_off_data = []
    for item in payload.time_off:
        time_off_data.append({
            "date": item.date,
            "reason": item.reason or "",
        })

    availability = create_or_update_coach_availability(
        db=db,
        coach_profile_id=profile.id,
        weekly=weekly_data,
        on_call=on_call_data,
        on_call_enabled=payload.on_call_enabled,
        time_off=time_off_data,
    )

    return format_availability_response(availability)
