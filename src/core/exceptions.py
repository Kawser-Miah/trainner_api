from typing import Any
from src.core.common_responses import ErrorResponse


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status: int = 400,
        error: Any = None,
        data: Any = None,
    ):
        super().__init__(message)

        self.message = message
        self.status = status
        self.error = error
        self.data = data


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

class InvalidCredentialsException(AppException):
    def __init__(
        self,
        message: str = "Invalid email or password.",
    ):
        super().__init__(
            error="INVALID_CREDENTIALS",
            message=message,
            status=401,
        )


class EmailNotVerifiedException(AppException):
    def __init__(
        self,
        user_id: str | int | None = None,
        message: str = "Please verify your email address before logging in.",
    ):
        payload_data = {"user_id": str(user_id)} if user_id is not None else None
        super().__init__(
            error="EMAIL_NOT_VERIFIED",
            message=message,
            status=403,
            data=payload_data,
        )


class InvalidOldPasswordException(AppException):
    def __init__(
        self,
        message: str = "Incorrect old password.",
    ):
        super().__init__(
            error="INVALID_OLD_PASSWORD",
            message=message,
            status=400,
        )


class InvalidPasswordException(AppException):
    def __init__(
        self,
        message: str = "Incorrect password.",
    ):
        super().__init__(
            error="INVALID_PASSWORD",
            message=message,
            status=400,
        )


class ForbiddenRoleException(AppException):
    def __init__(
        self,
        message: str = "Access denied. This service is restricted to providers only.",
    ):
        super().__init__(
            error="FORBIDDEN_ROLE",
            message=message,
            status=403,
        )


class CoachProfileNotFoundException(AppException):
    def __init__(
        self,
        message: str = "Coach profile not found.",
    ):
        super().__init__(
            error="COACH_PROFILE_NOT_FOUND",
            message=message,
            status=404,
        )

