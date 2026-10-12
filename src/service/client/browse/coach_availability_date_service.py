from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session

from src.repository.client.browse.client_browse_repository import (
    get_browse_coach_availability,
    get_browse_coach_service_detail,
)
from src.schemas.client.browse.availability_schemas import (
    CoachDateAvailabilityResponse,
    OnCallAvailabilityResponse,
    OnCallSlotItemResponse,
    OnCallWindowItem,
    TimeSlotItemResponse,
)


def format_12hr_time(hour: int, minute: int) -> str:
    am_pm = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{minute:02d} {am_pm}"


async def get_coach_availability_date_service(
    coach_profile_id: int,
    db: Session,
    date_str: str | None = None,
    service_id: int | None = None,
) -> dict:
    availability = get_browse_coach_availability(db=db, coach_profile_id=coach_profile_id)
    session_duration = 60
    if service_id:
        service = get_browse_coach_service_detail(db=db, service_id=service_id)
        if service and service.session_duration:
            session_duration = service.session_duration

    weekly = availability.weekly if availability and availability.weekly else []
    on_call_windows = availability.on_call if availability and availability.on_call else []
    on_call_enabled = bool(availability.on_call_enabled) if availability else True
    time_off = availability.time_off if availability and availability.time_off else []
    time_off_dates = {t.get("date") for t in time_off if isinstance(t, dict) and t.get("date")}

    if not weekly:
        weekly = [
            {"weekday": i, "start_time": "09:00", "end_time": "17:00"}
            for i in range(5)
        ]

    target_date_str = date_str or date.today().isoformat()
    try:
        parsed_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        parsed_date = date.today()
        target_date_str = parsed_date.isoformat()

    weekday_num = parsed_date.weekday()

    day_schedule = next((w for w in weekly if w.get("weekday") == weekday_num), None)
    slots: list[TimeSlotItemResponse] = []

    if day_schedule and target_date_str not in time_off_dates:
        start_t = day_schedule.get("start_time", "09:00")
        end_t = day_schedule.get("end_time", "17:00")
        start_h, start_m = map(int, start_t.split(":"))
        end_h, end_m = map(int, end_t.split(":"))

        current_min = start_h * 60 + start_m
        end_total_min = end_h * 60 + end_m - session_duration

        while current_min <= end_total_min:
            h = current_min // 60
            m = current_min % 60
            time_formatted = f"{h:02d}:{m:02d}"
            label = format_12hr_time(h, m)
            is_avail = (m % session_duration == 0) or (m == 0)
            slots.append(
                TimeSlotItemResponse(
                    time=time_formatted,
                    label=label,
                    available=is_avail,
                )
            )
            current_min += 15

    on_call_obj = None
    if on_call_enabled and target_date_str not in time_off_dates:
        windows = []
        on_call_slots = []
        matching_windows = [w for w in on_call_windows if w.get("weekday", weekday_num) == weekday_num]
        if not matching_windows:
            matching_windows = [{"start_time": "17:00", "end_time": "21:00"}]

        for win in matching_windows:
            w_start = win.get("start_time", "17:00")
            w_end = win.get("end_time", "21:00")
            windows.append(OnCallWindowItem(start_time=w_start, end_time=w_end))

            s_h, s_m = map(int, w_start.split(":"))
            e_h, e_m = map(int, w_end.split(":"))
            cur = s_h * 60 + s_m
            max_cur = e_h * 60 + e_m - session_duration

            while cur <= max_cur:
                hh = cur // 60
                mm = cur % 60
                slot_time = f"{hh:02d}:{mm:02d}"
                slot_label = format_12hr_time(hh, mm)

                slot_dt = datetime(parsed_date.year, parsed_date.month, parsed_date.day, hh, mm, tzinfo=timezone.utc)
                opens_at = (slot_dt - timedelta(hours=12)).isoformat()
                closes_at = (slot_dt - timedelta(hours=2)).isoformat()

                on_call_slots.append(
                    OnCallSlotItemResponse(
                        time=slot_time,
                        label=slot_label,
                        available=True,
                        can_request_now=False,
                        opens_at=opens_at,
                        closes_at=closes_at,
                    )
                )
                cur += 15

        on_call_obj = OnCallAvailabilityResponse(
            enabled=True,
            windows=windows,
            slots=on_call_slots,
        )

    return CoachDateAvailabilityResponse(
        coach_profile_id=coach_profile_id,
        session_duration=session_duration,
        has_availability=bool(slots),
        takes_on_call=on_call_enabled,
        date=target_date_str,
        weekday=weekday_num,
        slots=slots,
        on_call=on_call_obj,
    ).model_dump()
