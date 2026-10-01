from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.core.exceptions import InvalidTokenException


# JWT configuration
SECRET_KEY = (
    "this_is_a_secret_key_for_jwt_token_generation_and_should_be_changed_in_production"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(
    user_id: str,
    role: str,
    full_name: str,
) -> tuple[str, int]:
    """
    Create an access JWT token.

    Returns:
        tuple:
            token: JWT access token
            expires_at_ms: Expiration timestamp in milliseconds
    """

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

    # Convert expiration time to milliseconds
    expires_at_ms = int(expires_at.timestamp() * 1000)

    return token, expires_at_ms


def create_refresh_token(
    user_id: str,
) -> str:
    """
    Create a refresh JWT token.
    """

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


def verify_access_token(
    token: str,
) -> dict:
    """
    Verify and decode an access token.

    Raises:
        InvalidTokenException:
            If the token is invalid, expired, or not an access token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Make sure this is an access token
        if payload.get("type") != "access":
            raise InvalidTokenException()

        # Make sure user ID exists
        if payload.get("sub") is None:
            raise InvalidTokenException()

        return payload

    except JWTError:
        raise InvalidTokenException()


def verify_refresh_token(
    token: str,
) -> dict:
    """
    Verify and decode a refresh token.

    Raises:
        InvalidTokenException:
            If the token is invalid, expired, or not a refresh token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Make sure this is a refresh token
        if payload.get("type") != "refresh":
            raise InvalidTokenException()

        # Make sure user ID exists
        if payload.get("sub") is None:
            raise InvalidTokenException()

        return payload

    except JWTError:
        raise InvalidTokenException()