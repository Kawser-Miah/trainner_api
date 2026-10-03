from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.accounts.user import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    result = db.execute(
        select(User).where(
            User.email == email
        )
    )

    return result.scalar_one_or_none()


def create_user(
    db: Session,
    *,
    full_name: str,
    email: str,
    phone: str | None,
    password_hash: str,
    role: str,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=role,
        is_email_verified=False,
    )

    db.add(user)
    db.flush()

    return user

def get_user_by_id(
    db: Session,
    *,
    user_id: int,
) -> User | None:
    result = db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    return result.scalar_one_or_none()