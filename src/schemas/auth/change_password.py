from pydantic import BaseModel, model_validator
from src.core.exceptions import PasswordMismatchException


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    re_new_password: str

    @model_validator(mode="before")
    @classmethod
    def populate_re_new_password(cls, values):
        if isinstance(values, dict):
            if "re_new_password" not in values and "confirm_password" in values:
                values["re_new_password"] = values["confirm_password"]
        return values

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.re_new_password:
            raise PasswordMismatchException()

        return self
