from pydantic import BaseModel, Field, field_validator


class CreateCheckoutSessionRequest(BaseModel):
    booking_id: int = Field(..., description="The ID of the service order / booking.")
    success_url: str = Field(..., description="Redirect URL upon successful payment (must start with http:// or https://).")
    cancel_url: str = Field(..., description="Redirect URL upon payment cancellation (must start with http:// or https://).")
    credit_used: str | None = Field(default=None, description="Optional credit amount to apply.")

    @field_validator("success_url", "cancel_url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        trimmed = v.strip()
        if not (trimmed.startswith("http://") or trimmed.startswith("https://")):
            raise ValueError("URL must include an explicit scheme (e.g. https:// or http://).")
        return trimmed


class CheckoutSessionData(BaseModel):
    session_id: str
    checkout_url: str
    is_free: bool
    booking_id: int
    price: str
    client_fee: str
    client_fee_percent: str
    total: str
    credit_used: str
    payable: str
    currency: str


class CreateCheckoutSessionResponse(BaseModel):
    success: bool = True
    status: int = 200
    message: str = "Checkout session created successfully."
    data: CheckoutSessionData
