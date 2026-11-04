from pydantic import BaseModel, ConfigDict


class UserBillingHistoryItem(BaseModel):
    id: int
    type: str
    title: str
    coach_name: str
    coach_avatar: str | None = None
    amount: str
    currency: str = "USD"
    status: str
    booking_status: str
    booking_date: str | None = None
    paid_at: str | None = None
    refunded_at: str | None = None
    receipt_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserBillingHistoryData(BaseModel):
    total_spent: str
    sessions_this_month: int
    items: list[UserBillingHistoryItem]

    model_config = ConfigDict(from_attributes=True)


class UserBillingReceiptData(BaseModel):
    order_id: int
    receipt_number: str
    type: str
    title: str
    coach_name: str
    client_name: str
    amount: str
    client_fee: str
    total_amount: str
    currency: str
    status: str
    booking_status: str
    booking_date: str | None = None
    booking_time: str | None = None
    transaction_id: str | None = None
    paid_at: str | None = None
    refunded_at: str | None = None

    model_config = ConfigDict(from_attributes=True)

