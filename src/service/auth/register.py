from src.core.exceptions import EmailAlreadyExistsException
from src.utils.otp_generation import generate_otp
from src.utils.security import hash_password
from src.data.users import users, otps
from src.schemas.user.account import RegisterAccountRequest
from src.service.auth.email_service import send_otp_email
from starlette.concurrency import run_in_threadpool


async def register_user(
    register_account_request: RegisterAccountRequest,
):
    # Check whether email already exists
    for user in users:
        if user["email"] == str(register_account_request.email):
            raise EmailAlreadyExistsException()

    # Generate OTP
    otp = generate_otp()

    # Create user
    user = {
        "id": str(len(users) + 1),
        "full_name": register_account_request.full_name,
        "role": register_account_request.role,
        "email": str(register_account_request.email),
        "phone": register_account_request.phone,
        "password": await run_in_threadpool(
            hash_password,
            register_account_request.password
        ),
        "is_verified": False,
    }

    otp_entry = {
        "user_id": user["id"],
        "otp": otp,
    }

    # Store user
    users.append(user)
    otps.append(otp_entry)

    # Send OTP
    await send_otp_email(
        email=user["email"],
        otp=otp,
    )

    return user