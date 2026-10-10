from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.provider.coach_profile.coach_availability import CoachAvailability


def get_coach_availability_by_profile_id(
    db: Session, coach_profile_id: int
) -> CoachAvailability | None:
    return db.execute(
        select(CoachAvailability).where(CoachAvailability.coach_profile_id == coach_profile_id)
    ).scalar_one_or_none()


def create_or_update_coach_availability(
    db: Session,
    coach_profile_id: int,
    weekly: list[dict],
    on_call: list[dict],
    on_call_enabled: bool,
    time_off: list[dict],
) -> CoachAvailability:
    availability = get_coach_availability_by_profile_id(db, coach_profile_id)
    if availability is None:
        availability = CoachAvailability(
            coach_profile_id=coach_profile_id,
            weekly=weekly,
            on_call=on_call,
            on_call_enabled=on_call_enabled,
            time_off=time_off,
        )
        db.add(availability)
    else:
        availability.weekly = weekly
        availability.on_call = on_call
        availability.on_call_enabled = on_call_enabled
        availability.time_off = time_off

    db.commit()
    db.refresh(availability)
    return availability
