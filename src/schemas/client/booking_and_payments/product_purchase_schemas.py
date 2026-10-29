from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.client.booking_and_payments.booking_schemas import (
    OrderCoachResponse,
    OrderUserResponse,
)


class PurchaseProductRequest(BaseModel):
    product_id: int = Field(..., description="ID of the digital product to purchase")
    referral_code: str | None = Field(default="", description="Optional referral code")


class OrderProductDetail(BaseModel):
    id: int
    title: str
    description: str = ""
    price: str = "0.00"
    Thumbnail: str | None = Field(default=None, serialization_alias="Thumbnail")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProductPurchaseResponseData(BaseModel):
    id: int
    user: OrderUserResponse
    coach: OrderCoachResponse
    service: Any | None = None
    product: OrderProductDetail | None = None
    order_type: str = "product"
    booking_date: str | None = None
    booking_time: str | None = None
    amount: str
    client_fee: str = "0.00"
    client_fee_percent: str = "0.00"
    total_amount: str
    coach_fee: str
    coach_fee_percent: str
    coach_earning: str
    currency: str = "USD"
    status: str = "pending"
    payment_status: str = "pending"
    payment_method: str | None = None
    transaction_id: str | None = None
    notes: str | None = None
    can_join: bool = False
    coach_message: str = ""
    is_on_call: bool = False
    payment_due_at: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

