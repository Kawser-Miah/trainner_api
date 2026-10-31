from pydantic import BaseModel, ConfigDict


class UserBookingItem(BaseModel):
    id: int
    provider_user_id: int
    coach_profile_id: int
    coach_name: str = ""
    coach_profile_photo: str | None = None
    service_id: int | None = None
    service_title: str = ""
    service_category: str = ""
    service_type: str = "one_time"
    session_format: str = "video"
    session_duration: int = 60
    can_join: bool = False
    preparation_instructions: str = ""
    booking_date: str | None = None
    booking_time: str | None = None
    amount: str
    currency: str = "USD"
    cancellation_policy: str = ""
    status: str
    payment_status: str
    payment_method: str | None = None
    is_rescheduled: bool = False
    notes: str | None = None
    coach_message: str = ""
    has_reviewed: bool = False
    can_cancel: bool = False
    can_reschedule: bool = False

    model_config = ConfigDict(from_attributes=True)
