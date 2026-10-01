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
class InvalidOTPException(AppException):
    def __init__(self):
        super().__init__(
            error="INVALID_OTP",
            message="The OTP is invalid or has expired.",
            status=400,
        )

class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            error="USER_NOT_FOUND",
            message="The user was not found.",
            status=404,
        )

class OTPNotExpiredException(AppException):
    def __init__(self):
        super().__init__(
            error="OTP_NOT_EXPIRED",
            message="The previous OTP is still valid. Please wait until it expires before requesting a new one.",
            status=400,
        )

class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            error="INVALID_TOKEN",
            message="The provided token is invalid or has expired.",
            status=400,
        )