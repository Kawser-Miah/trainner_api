from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BookServiceRequest(BaseModel):
    service_id: int = Field(..., description="ID of the service to book")
    booking_date: str = Field(..., description="Date of booking (e.g. YYYY-MM-DD)")
    booking_time: str = Field(..., description="Time of booking (e.g. 02:00 PM)")
    referral_code: str | None = Field("", description="Optional referral code")


class OrderUserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str = ""

    model_config = ConfigDict(from_attributes=True)


class OrderCoachResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str = ""
    profile_photo: str | None = None
    about: str = ""

    model_config = ConfigDict(from_attributes=True)


class OrderCategoryResponse(BaseModel):
    id: int
    name: str
    description: str = ""

    model_config = ConfigDict(from_attributes=True)


class OrderServiceResponse(BaseModel):
    id: int
    title: str
    description: str = ""
    service_type: str = "one_time"
    session_format: str = "video"
    session_duration: int = 60
    price: str = "0.00"
    currency: str = "USD"
    booking_type: str = "instant"
    session_url: str | None = None
    category: OrderCategoryResponse

    model_config = ConfigDict(from_attributes=True)


class ServiceOrderDetailResponse(BaseModel):
    id: int
    user: OrderUserResponse
    coach: OrderCoachResponse
    service: OrderServiceResponse | None = None
    product: Any | None = None
    order_type: str = "service"
    booking_date: str | None = None
    booking_time: str | None = None
    amount: str
    client_fee: str
    client_fee_percent: str
    total_amount: str
    coach_fee: str
    coach_fee_percent: str
    coach_earning: str
    currency: str
    status: str
    payment_status: str
    payment_method: str | None = None
    transaction_id: str | None = None
    is_on_call: bool = False
    payment_due_at: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
