from pydantic import BaseModel, ConfigDict, Field
from src.core.common_responses import CommonResponse


WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def get_weekday_display(weekday: int) -> str:
    return WEEKDAY_NAMES.get(weekday, "")


class AvailabilityTimeSlotItem(BaseModel):
    weekday: int
    weekday_display: str | None = None
    start_time: str
    end_time: str

    model_config = ConfigDict(from_attributes=True)


class AvailabilityTimeOffItem(BaseModel):
    date: str
    reason: str | None = ""

    model_config = ConfigDict(from_attributes=True)


class UpdateCoachAvailabilityRequest(BaseModel):
    weekly: list[AvailabilityTimeSlotItem] = Field(default_factory=list)
    on_call: list[AvailabilityTimeSlotItem] = Field(default_factory=list)
    on_call_enabled: bool = True
    time_off: list[AvailabilityTimeOffItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CoachAvailabilityDataResponse(BaseModel):
    has_availability: bool = False
    weekly: list[AvailabilityTimeSlotItem] = Field(default_factory=list)
    on_call: list[AvailabilityTimeSlotItem] = Field(default_factory=list)
    on_call_enabled: bool = True
    time_off: list[AvailabilityTimeOffItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


CoachAvailabilityResponse = CommonResponse
