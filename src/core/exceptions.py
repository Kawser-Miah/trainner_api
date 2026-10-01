from typing import Any
from src.core.common_responses import ErrorResponse


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status: int = 400,
        error: Any = None,
    ):
        super().__init__(message)

        self.message = message
        self.status = status
        self.error = error


class PasswordMismatchException(AppException):
    def __init__(self):
        super().__init__(
            message="Password and confirm password do not match.",
            status=400,
            error="PASSWORD_MISMATCH",
        )


class EmailAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="An account with this email already exists.",
            status=409,
            error="EMAIL_ALREADY_EXISTS",
        )