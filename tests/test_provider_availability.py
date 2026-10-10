import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.coach_profile import CoachProfile, CoachAvailability
from src.utils.jwt import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_coach_user(db_session):
    user = db_session.execute(
        select(User).where(User.email == "test_availability_coach@coachhub.com")
    ).scalar_one_or_none()

    if not user:
        user = User(
            full_name="Availability Coach",
            email="test_availability_coach@coachhub.com",
            password_hash="test_hashed_password",
            phone="+1234567890",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    existing_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == user.id)
    ).scalar_one_or_none()

    if not existing_profile:
        profile = CoachProfile(
            user_id=user.id,
            headline="Master Coach",
            about="Expert in scheduling",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    return user


def test_put_and_get_coach_availability(test_coach_user, db_session):
    client = TestClient(app)
    token, _ = create_access_token(
        user_id=test_coach_user.id,
        role=test_coach_user.role,
        full_name=test_coach_user.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "weekly": [
            {
                "weekday": 0,
                "start_time": "09:00",
                "end_time": "17:00"
            },
            {
                "weekday": 2,
                "start_time": "10:00",
                "end_time": "14:00"
            }
        ],
        "on_call": [
            {
                "weekday": 0,
                "start_time": "17:00",
                "end_time": "21:00"
            }
        ],
        "on_call_enabled": True,
        "time_off": [
            {
                "date": "2026-10-16",
                "reason": "Holiday"
            }
        ]
    }

    # 1. Update Availability (PUT /api/Provider/coach-availability)
    response = client.put(
        "/api/Provider/coach-availability",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["message"] == "Availability updated successfully."

    data = res_data["data"]
    assert data["has_availability"] is True
    assert data["on_call_enabled"] is True
    assert len(data["weekly"]) == 2
    assert data["weekly"][0]["weekday"] == 0
    assert data["weekly"][0]["weekday_display"] == "Monday"
    assert data["weekly"][0]["start_time"] == "09:00"
    assert data["weekly"][0]["end_time"] == "17:00"

    assert data["weekly"][1]["weekday"] == 2
    assert data["weekly"][1]["weekday_display"] == "Wednesday"

    assert len(data["on_call"]) == 1
    assert data["on_call"][0]["weekday_display"] == "Monday"

    assert len(data["time_off"]) == 1
    assert data["time_off"][0]["date"] == "2026-10-16"
    assert data["time_off"][0]["reason"] == "Holiday"

    # 2. Get Availability (GET /api/Provider/coach-availability)
    get_res = client.get("/api/Provider/coach-availability", headers=headers)
    assert get_res.status_code == 200, get_res.text
    get_data = get_res.json()["data"]
    assert get_data["has_availability"] is True
    assert len(get_data["weekly"]) == 2
    assert get_data["weekly"][0]["weekday_display"] == "Monday"
