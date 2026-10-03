from pydantic import BaseModel, model_validator
from src.core.exceptions import PasswordMismatchException


class ResetPasswordRequest(BaseModel):
    secret_key: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise PasswordMismatchException()

        return self