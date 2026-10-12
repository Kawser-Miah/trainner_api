from typing import Any
from pydantic import BaseModel, ConfigDict


class TimeSlotItemResponse(BaseModel):
    time: str
    label: str
    available: bool

    model_config = ConfigDict(from_attributes=True)


class OnCallSlotItemResponse(BaseModel):
    time: str
    label: str
    available: bool
    can_request_now: bool = False
    opens_at: str | None = None
    closes_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OnCallWindowItem(BaseModel):
    start_time: str
    end_time: str


class OnCallAvailabilityResponse(BaseModel):
    enabled: bool = True
    windows: list[OnCallWindowItem] = []
    slots: list[OnCallSlotItemResponse] = []


class CoachDateAvailabilityResponse(BaseModel):
    coach_profile_id: int
    session_duration: int = 60
    has_availability: bool = True
    takes_on_call: bool = True
    date: str
    weekday: int
    slots: list[TimeSlotItemResponse] = []
    on_call: OnCallAvailabilityResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CoachMonthAvailabilityResponse(BaseModel):
    coach_profile_id: int
    session_duration: int = 60
    has_availability: bool = True
    takes_on_call: bool = True
    month: str
    available_dates: list[str] = []

    model_config = ConfigDict(from_attributes=True)
