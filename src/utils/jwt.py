from datetime import datetime, timedelta, timezone

from jose import jwt

SECRET_KEY = "this_is_a_secret_key_for_jwt_token_generation_and_should_be_changed_in_production"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(user_id: str, role:str, full_name:str) -> tuple[str, int]:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "role": role,
        "full_name": full_name,
        "type": "access",
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # Unix timestamp in milliseconds
    expires_at_ms = int(expires_at.timestamp() * 1000)

    return token, expires_at_ms


def create_refresh_token(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )