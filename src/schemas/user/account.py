from pydantic import BaseModel, EmailStr, Field, model_validator
from src.core.exceptions import PasswordMismatchException


class RegisterAccountRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    role: str = Field(..., min_length=2, max_length=20)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.confirm_password:
            raise PasswordMismatchException()

        return self


class RegisterAccountResponse(BaseModel):
    user_id: str | None = None